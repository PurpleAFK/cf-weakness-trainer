# cf-weakness-trainer

CF Practice Coach: pulls a user's Codeforces submission history, profiles their weak tags and rating bands from verdict patterns, and recommends targeted problems.

## TODO

Done:
- [x] `fetch_data.py`: paginated `user.status`, `user.rating`, `problemset.problems`, 2.2s rate limiter, raw JSON snapshots in `data/raw/`
- [x] `audit.py`: exploratory pandas on own submissions (verdict counts, `json_normalize`, dedupe problems, count missing ratings)
- [x] Cohort rule written down in `NOTES.md`

Cleanup:
- [ ] `fetch_data.py`: handle passed as an argument instead of `HANDLE = input(...)` at module scope (importing it currently blocks on a prompt)
- [ ] `audit.py`: wrapped in a function, no hardcoded snapshot path in `data/raw/`
- [ ] Skip rule settled: `NOTES.md` says "<5 contests **and** 50 problems", the plan says **or**
- [ ] `requirements.txt` trimmed to direct dependencies (or marked as a full freeze)

Core recommender:
- [ ] Cohort: standings of the 3 most recent Div. 2 contests → rating 800–1600 → first ~20–25 handles → apply the skip rule
- [ ] Cohort data fetched and snapshotted
- [ ] Weakness profiler: per-tag and per-rating-band solve rate / attempts-before-AC from verdicts
- [ ] Recommender: unsolved problems in weak tags at a rating just above the comfort band
- [ ] Tests for the profiler and recommender (small fixture JSON)

UI and deploy:
- [ ] Streamlit app that calls the Python functions directly (no FastAPI in v1)
- [ ] Un-containerized deploy (e.g. Streamlit Community Cloud)

LLM layer:
- [ ] Open-source model (Llama or Qwen via Ollama or Groq) explains weak tags and gives hints
- [ ] Structured JSON output with schema validation and retry on bad JSON
- [ ] No secrets or user data in logs

RAG (cut if not working):
- [ ] CP notes/editorials (e.g. CPH) chunked, embedded and stored in a vector store
- [ ] Retrieved chunks fed into the hint prompt; chunk size and model choice written down with reasons

Evals:
- [ ] 10–20 test cases comparing outputs to expected behavior
- [ ] At least one prompt-injection case

Ship:
- [ ] Dockerfile (after the un-containerized deploy works)
- [ ] README: setup, usage, architecture diagram, design decisions
- [ ] Resume updated with only what actually works

Stretch (not before the interview):
- [ ] Agent loop: LLM calling tools such as fetch-user-stats and search-problems
