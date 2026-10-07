"""Retrieval eval: compare search strategies on the knowledge base (no LLM needed).

Run:  python -m evals.retrieval_eval      -> prints a table and writes evals/RETRIEVAL.md

For every Codeforces tag the notes cover, a strategy "hits" if the top chunk comes from a note
tagged with it. For tags the notes do NOT cover, the right behavior is to return nothing; a strategy
that returns a chunk anyway feeds the model irrelevant context.
"""

from pathlib import Path

import rag

UNCOVERED = ["2-sat", "flows", "geometry", "probabilities", "fft", "matrices", "interactive"]


def main():
    store, emb = rag.VectorStore.load(), rag.FastEmbedder()
    covered = sorted({t for c in store.chunks for t in c.tags})

    def generic(tag):
        return rag.query_for({"tag": tag, "kind": "weak"})

    strategies = {
        "dense, generic query": lambda t: store.search(emb.embed_query(generic(t)), k=2),
        "dense, tag-only query": lambda t: store.search(emb.embed_query(t), k=2),
        "hybrid: tag filter + dense rank (used)": lambda t: store.search(
            emb.embed_query(generic(t)), k=2, tag=t
        ),
    }

    rows = []
    for name, search in strategies.items():
        hit1 = hit2 = 0
        covered_scores = []
        for t in covered:
            res = search(t)
            hit1 += bool(res) and t in res[0][0].tags
            hit2 += any(t in c.tags for c, _ in res)
            covered_scores += [s for _, s in res[:1]]
        unc = [search(t) for t in UNCOVERED]
        unc_scores = [r[0][1] for r in unc if r]
        rows.append(
            {
                "strategy": name,
                "hit@1": f"{hit1}/{len(covered)}",
                "hit@2": f"{hit2}/{len(covered)}",
                "uncovered tags given context": f"{sum(bool(r) for r in unc)}/{len(UNCOVERED)}",
                "top score, covered (min)": f"{min(covered_scores):.2f}",
                "top score, uncovered (max)": f"{max(unc_scores):.2f}" if unc_scores else "-",
            }
        )

    # Section choice inside a topic: weak tags should get the "mistakes" section first.
    weak_ok = total = 0
    for t in covered:
        notes = [c for c in store.chunks if t in c.tags]
        if any("mistake" in c.title.lower() or "avoid" in c.title.lower() for c in notes):
            total += 1
            top = store.search(emb.embed_query(generic(t)), k=1, tag=t)[0][0]
            weak_ok += "mistake" in top.title.lower() or "avoid" in top.title.lower()

    cols = list(rows[0])
    lines = [
        "# Retrieval eval",
        "",
        f"{len(store.chunks)} chunks, {len(covered)} covered tags, {len(UNCOVERED)} uncovered tags "
        f"({', '.join(UNCOVERED)}). Embedding model: `{store.model}`.",
        "",
        "| " + " | ".join(cols) + " |",
        "|" + "---|" * len(cols),
        *("| " + " | ".join(r[c] for c in cols) + " |" for r in rows),
        "",
        f"Hybrid, weak-tag query: the top chunk is the note's mistakes section for "
        f"{weak_ok}/{total} tags whose note has one.",
        "",
        "Reading it: pure dense search always returns *something*, and its scores for uncovered "
        "tags overlap the scores for covered ones, so a similarity threshold can't detect 'no "
        "relevant note'. The metadata filter decides the topic; embeddings pick the section.",
    ]
    out = "\n".join(lines) + "\n"
    (Path(__file__).parent / "RETRIEVAL.md").write_text(out)
    print(out)


if __name__ == "__main__":
    main()
