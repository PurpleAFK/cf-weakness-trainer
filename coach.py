"""End to end: handle -> submissions -> weakness profile -> recommended problems.

Usage:  python coach.py <handle> [-n 10] [--refresh]
"""

import argparse
import re
from datetime import date
from pathlib import Path

import fetch_data
from profiler import build_attempts, rating_band_profile
from recommender import problem_pool, recommend
from snapshots import latest_snapshot, load_json

# Codeforces handles: 3-24 characters of letters, digits, '_', '-', '.'.
HANDLE_RE = re.compile(r"^[A-Za-z0-9_.\-]{3,24}$")
BASELINE_PATH = Path(__file__).parent / "cohort_baseline.json"


def valid_handle(handle):
    return bool(HANDLE_RE.fullmatch(handle or ""))


def _cached(endpoint, handle, fetch_fn, raw_dir, refresh):
    """Today's snapshot if we already have one, otherwise call the API and save a new one."""
    today = Path(raw_dir) / f"{date.today()}_{endpoint}_{handle}.json"
    if today.exists() and not refresh:
        return load_json(today)
    return load_json(fetch_data.save_raw(endpoint, handle, fetch_fn(), raw_dir))


def load_problemset(raw_dir="data/raw", refresh=False):
    """The problemset changes slowly: reuse any existing snapshot unless asked to refresh."""
    if not refresh:
        try:
            return load_json(latest_snapshot("problemset.problems", raw_dir=raw_dir))
        except FileNotFoundError:
            pass
    return _cached("problemset.problems", "all", fetch_data.fetch_problemset, raw_dir, True)


def load_user(handle, raw_dir="data/raw", refresh=False):
    if not valid_handle(handle):
        raise ValueError(f"not a valid Codeforces handle: {handle!r}")
    status = _cached(
        "user.status", handle, lambda: fetch_data.fetch_all_status(handle), raw_dir, refresh
    )
    rating = _cached(
        "user.rating", handle, lambda: fetch_data.fetch_rating(handle), raw_dir, refresh
    )
    return status, rating


def load_baseline():
    return load_json(BASELINE_PATH) if BASELINE_PATH.exists() else None


def analyze(status, rating_history, problemset, n=10, baseline=None):
    """Pure function (no I/O) so the CLI, the Streamlit app and the tests share it."""
    attempts = build_attempts(status)
    current = rating_history[-1]["newRating"] if rating_history else None
    recs, ctx = recommend(attempts, problem_pool(problemset), current, n=n, baseline=baseline)
    ctx.update(
        attempts=attempts,
        bands=rating_band_profile(attempts),
        current_rating=current,
        baseline_used=baseline is not None,
    )
    return recs, ctx


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("handle")
    parser.add_argument("-n", type=int, default=10)
    parser.add_argument("--refresh", action="store_true", help="ignore today's cached snapshots")
    args = parser.parse_args()

    status, rating = load_user(args.handle, refresh=args.refresh)
    recs, ctx = analyze(status, rating, load_problemset(), args.n, load_baseline())

    lo, hi = ctx["target_range"]
    print(f"{args.handle}: rating {ctx['current_rating']}, practice window {lo}-{hi}")
    print(
        f"{len(ctx['attempts'])} problems attempted, {int(ctx['attempts']['solved'].sum())} solved"
    )
    print("\nWeak tags:")
    for r in ctx["weak_tags"].itertuples():
        print(f"  {r.tag:<25} {r.solved}/{r.attempted} solved  weakness {r.weakness:+.2f}")
    print("Under-practiced tags:")
    for r in ctx["underexposed_tags"].itertuples():
        print(f"  {r.tag:<25} you {r.user_share:.0%} vs window {r.pool_share:.0%}")
    print("\nRecommended:")
    for r in recs.itertuples():
        print(f"  {r.problem_id:<7} {r.rating}  {r.name[:40]:<40} [{r.focus_tag}]  {r.url}")


if __name__ == "__main__":
    main()
