"""Retrieval-augmented generation over the CP technique notes in knowledge/.

Offline (python rag.py): split notes into chunks -> embed each chunk -> save the vectors and the
chunk metadata to knowledge/index.npz + knowledge/index.json (committed, ~100 KB).
Online (hybrid retrieval): keep only chunks whose note is tagged with the focus tag (metadata
filter) -> embed a query for that tag -> rank those chunks by cosine similarity -> top-k go into the
LLM prompt (llm.py) so hints are grounded in real notes. A tag with no notes gets no chunks.

Why hybrid and not pure semantic search (measured in evals/retrieval_eval.py): with generic query
text, one "avoid wrong submissions" chunk ranked first for many unrelated tags, and similarity
scores for covered and uncovered tags overlapped (0.64-0.72), so no threshold could tell "no
relevant note" apart from "relevant note". The metadata filter answers *which topic*; the embeddings
answer *which section* (common mistakes for weak tags, basics for under-practiced ones).

Chunking: one chunk per "## " section. Each section is written as one self-contained idea of
~55-110 words (~70-150 tokens): far under the embedding model's 512-token limit (no truncation),
one topic per vector, and a small prompt (<= 2 chunks per tag, <= 10 chunks in total).
Each chunk is prefixed with its document title ("Binary search > Common mistakes ...") so the
embedding knows the topic even when the section text doesn't repeat it.
"""

import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np

KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"
EMBED_MODEL = "BAAI/bge-small-en-v1.5"  # 384-dim, ~130 MB ONNX, runs on CPU in-process
MAX_WORDS = 300  # longer sections are split on paragraph boundaries
TOP_K = 2


@dataclass
class Chunk:
    id: str  # "<file stem>#<section number>", e.g. "binary-search#2"
    title: str  # "Binary search > Binary search on the answer"
    text: str
    tags: list[str]  # Codeforces tags the note is about (metadata, shown in the UI)


def chunk_markdown(path):
    """Split one note into section chunks.

    Note format: '# Title', then 'tags: a, b', then '## ...' sections.
    """
    lines = Path(path).read_text().splitlines()
    doc_title = lines[0].removeprefix("# ").strip()
    tags = []
    if len(lines) > 1 and lines[1].startswith("tags:"):
        tags = [t.strip() for t in lines[1].removeprefix("tags:").split(",") if t.strip()]

    sections, heading, body = [], None, []
    for line in lines[1:]:
        if line.startswith("## "):
            if heading:
                sections.append((heading, body))
            heading, body = line.removeprefix("## ").strip(), []
        elif heading:
            body.append(line)
    if heading:
        sections.append((heading, body))

    chunks = []
    for heading, body in sections:
        paragraphs = [p.strip() for p in "\n".join(body).split("\n\n") if p.strip()]
        for part in _split_long(paragraphs):
            chunks.append(
                Chunk(
                    id=f"{Path(path).stem}#{len(chunks) + 1}",
                    title=f"{doc_title} > {heading}",
                    text=" ".join(part),
                    tags=tags,
                )
            )
    return chunks


def _split_long(paragraphs, max_words=MAX_WORDS):
    """Group paragraphs into parts of at most max_words (a single long paragraph stays whole)."""
    parts, current, words = [], [], 0
    for p in paragraphs:
        n = len(p.split())
        if current and words + n > max_words:
            parts.append(current)
            current, words = [], 0
        current.append(p)
        words += n
    if current:
        parts.append(current)
    return parts


def load_chunks(knowledge_dir=KNOWLEDGE_DIR):
    return [c for f in sorted(Path(knowledge_dir).glob("*.md")) for c in chunk_markdown(f)]


def embed_text(chunk):
    """What gets embedded: the title gives the section its topic."""
    return f"{chunk.title}\n{chunk.text}"


def fingerprint(chunks, model):
    """Changes whenever a note or the model changes, so a stale index is detected."""
    h = hashlib.sha256(model.encode())
    for c in chunks:
        h.update(embed_text(c).encode())
    return h.hexdigest()[:16]


class FastEmbedder:
    """bge-small via fastembed (ONNX runtime, no PyTorch). Downloads the model on first use."""

    def __init__(self, model=EMBED_MODEL):
        from fastembed import TextEmbedding  # imported lazily: heavy, and tests don't need it

        self.model = model
        self._m = TextEmbedding(model)

    def embed_passages(self, texts):
        return _normalize(np.array(list(self._m.passage_embed(texts)), dtype=np.float32))

    def embed_query(self, text):
        # bge models expect queries and passages to be embedded slightly differently
        return _normalize(np.array(list(self._m.query_embed([text])), dtype=np.float32))[0]


def _normalize(m):
    """Unit-length rows, so cosine similarity is just a dot product."""
    norms = np.linalg.norm(m, axis=-1, keepdims=True)
    return m / np.maximum(norms, 1e-12)


class VectorStore:
    """Brute-force exact search: a (n_chunks x dim) matrix and one matrix-vector product per query.

    With ~70 chunks this takes microseconds. At ~1e5+ chunks you'd switch to an approximate index
    (FAISS / HNSW) or a database with vector search (pgvector, Chroma, Qdrant).
    """

    def __init__(self, chunks, vectors, model="", fp=""):
        assert len(chunks) == len(vectors)
        self.chunks, self.vectors = list(chunks), np.asarray(vectors, dtype=np.float32)
        self.model, self.fingerprint = model, fp

    def search(self, query_vec, k=TOP_K, tag=None):
        """Top-k (chunk, cosine score). With tag, only chunks whose note carries that tag."""
        idx = [i for i, c in enumerate(self.chunks) if tag is None or tag in c.tags]
        if not idx:
            return []
        scores = self.vectors[idx] @ query_vec
        order = np.argsort(-scores)[:k]
        return [(self.chunks[idx[j]], float(scores[j])) for j in order]

    def add(self, chunk, vector):
        self.chunks.append(chunk)
        self.vectors = np.vstack([self.vectors, vector[None, :]])

    def save(self, directory=KNOWLEDGE_DIR):
        np.savez_compressed(Path(directory) / "index.npz", vectors=self.vectors)
        meta = {
            "model": self.model,
            "fingerprint": self.fingerprint,
            "chunks": [asdict(c) for c in self.chunks],
        }
        (Path(directory) / "index.json").write_text(json.dumps(meta, indent=1) + "\n")

    @classmethod
    def load(cls, directory=KNOWLEDGE_DIR):
        meta = json.loads((Path(directory) / "index.json").read_text())
        vectors = np.load(Path(directory) / "index.npz")["vectors"]
        chunks = [Chunk(**c) for c in meta["chunks"]]
        return cls(chunks, vectors, meta["model"], meta["fingerprint"])


def build_index(embedder, knowledge_dir=KNOWLEDGE_DIR):
    chunks = load_chunks(knowledge_dir)
    vectors = embedder.embed_passages([embed_text(c) for c in chunks])
    return VectorStore(chunks, vectors, embedder.model, fingerprint(chunks, embedder.model))


class Retriever:
    def __init__(self, store, embedder, k=TOP_K):
        self.store, self.embedder, self.k = store, embedder, k

    def retrieve(self, query, tag=None):
        return self.store.search(self.embedder.embed_query(query), self.k, tag)

    def for_focus(self, focus):
        """Chunks for one focus tag from llm.build_profile(), best first."""
        return self.retrieve(query_for(focus), tag=focus["tag"])


def query_for(focus):
    """Within the tag's notes: mistakes for a weak tag, the basics for an under-practiced one."""
    if focus["kind"] == "weak":
        return f"{focus['tag']}: common mistakes and how to avoid wrong submissions"
    return f"{focus['tag']}: the basic technique and how to start practicing it"


# Instruction-like text has no place in technique notes. A note that matches is dropped before it
# reaches the prompt or the fallback (defense against a poisoned knowledge base; see evals c14).
INJECTION_RE = re.compile(
    r"ignore (all |any |the )?(previous |prior |above )?(instructions|rules)"
    r"|system (override|prompt|message|note)|disregard|you are now|https?://|www\."
    r"|\b[\w-]+\.(com|net|org|io|xyz|ru)\b",
    re.IGNORECASE,
)


def looks_like_injection(text):
    return bool(INJECTION_RE.search(text))


_retriever = None


def default_retriever():
    """Shared retriever for the app/CLI; rebuilds a stale index. Returns None on failure."""
    global _retriever
    if _retriever is None:
        try:
            embedder = FastEmbedder()
            try:
                store = VectorStore.load()
                if store.fingerprint != fingerprint(load_chunks(), embedder.model):
                    raise ValueError("stale index")
            except (FileNotFoundError, ValueError, KeyError):
                store = build_index(embedder)
            _retriever = Retriever(store, embedder)
        except Exception:  # missing package, no network for the model download, ...
            return None
    return _retriever


def main():
    chunks = load_chunks()
    words = [len(c.text.split()) for c in chunks]
    print(
        f"{len(chunks)} chunks from {len(set(c.id.split('#')[0] for c in chunks))} notes; "
        f"words per chunk: min {min(words)}, median {sorted(words)[len(words) // 2]}, "
        f"max {max(words)}"
    )
    store = build_index(FastEmbedder())
    store.save()
    print(f"saved knowledge/index.npz ({store.vectors.shape}) and knowledge/index.json")


if __name__ == "__main__":
    main()
