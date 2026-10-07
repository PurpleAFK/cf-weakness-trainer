# Retrieval eval

63 chunks, 21 covered tags, 7 uncovered tags (2-sat, flows, geometry, probabilities, fft, matrices, interactive). Embedding model: `BAAI/bge-small-en-v1.5`.

| strategy | hit@1 | hit@2 | uncovered tags given context | top score, covered (min) | top score, uncovered (max) |
|---|---|---|---|---|---|
| dense, generic query | 14/21 | 19/21 | 7/7 | 0.69 | 0.72 |
| dense, tag-only query | 21/21 | 21/21 | 7/7 | 0.64 | 0.66 |
| hybrid: tag filter + dense rank (used) | 21/21 | 21/21 | 0/7 | 0.66 | - |

Hybrid, weak-tag query: the top chunk is the note's mistakes section for 8/12 tags whose note has one.

Reading it: pure dense search always returns *something*, and its scores for uncovered tags overlap the scores for covered ones, so a similarity threshold can't detect 'no relevant note'. The metadata filter decides the topic; embeddings pick the section.
