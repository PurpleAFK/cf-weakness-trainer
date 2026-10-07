# cf-weakness-trainer

CF Practice Coach: pulls a user's Codeforces submission history, profiles their weak tags and rating bands from verdict patterns, and recommends targeted problems.

## How it works

```
Codeforces API ──> fetch_data.py ──> data/raw/*.json snapshots
                       │
                       v
               profiler.py: submissions -> attempts (one row per problem)
                            -> per-tag profile (smoothed solve rate, wrong submits, weakness)
                            -> rating bands, practice window
                       │            ^
                       │            └── cohort_baseline.json (per-tag averages of ~25 peers, cohort.py)
                       v
               recommender.py: weak + under-practiced tags -> unsolved problems in the window
                       │
                       v
               llm.py (optional): profile -> LLM -> validated JSON coaching notes (or fallback)
                       │
                       v
               app.py (Streamlit)  /  coach.py (CLI)
```

- **Attempt:** one row per problem. Wrong submits are counted only before the first AC; compilation
  errors are ignored.
- **Weakness score:** `difficulty = (1 - solve rate) + 0.15 * wrong submits per problem`, and
  `weakness = difficulty(you) - difficulty(reference)`. The reference is the cohort's average for that
  tag (or your own overall average without a baseline). Small samples are smoothed with 3
  pseudo-attempts at the reference rate. A tag needs at least 3 attempts and weakness >= 0.05.
- **Under-practiced tag:** its share of your problems is less than half its share among problems in
  your practice window.
- **Practice window:** `max(current rating, median rating of your last 30 solves)`, rounded down to
  100, then +100 to +300.
- **Ordering:** problems you tried and failed come first, then a rating ladder (most-solved problem at
  each rating), with focus tags taking turns.
- **LLM notes:** only aggregate stats are sent. The reply must match a pydantic schema and mention
  exactly the focus tags. Otherwise it is retried once with the error, then replaced by a rule-based
  summary.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
```

## Usage

```bash
python coach.py <handle>          # CLI report
streamlit run app.py              # web UI on http://localhost:8501
python cohort.py                  # rebuild cohort_baseline.json (~10 minutes, rate-limited)
pytest                            # tests use fake data, no network
```

Optional LLM notes (any OpenAI-compatible endpoint):

```bash
export GROQ_API_KEY=...                 # hosted, free tier: https://console.groq.com
# or, fully local:
export LLM_PROVIDER=ollama              # with `ollama serve` running and the model pulled
export LLM_MODEL=qwen2.5:7b-instruct    # optional model override
```

## Files

| File | Role |
|---|---|
| `fetch_data.py` | Rate-limited (2.2 s) Codeforces API client, pagination, raw snapshots |
| `snapshots.py` | Find and load the newest snapshot |
| `profiler.py` | Attempts, per-tag profile, rating bands, practice window, cohort baseline |
| `recommender.py` | Problem pool, under-practiced tags, recommendations |
| `coach.py` | End-to-end pipeline + CLI, handle validation, snapshot caching |
| `cohort.py` | Builds the ~25-user cohort and `cohort_baseline.json` |
| `llm.py` | Prompt, schema, validation/retry/fallback, OpenAI-compatible client |
| `app.py` | Streamlit UI |
| `audit.py` | Early exploratory script |

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
