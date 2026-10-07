"""Build the comparison cohort and its per-tag baseline.

Rule (NOTES.md): rated participants of the 3 most recent Div. 2 contests whose rating after the
contest was 800-1600, in a seeded random order, first COHORT_SIZE handles that pass the skip rule
(skip anyone with < 5 rated contests OR < 50 solved problems).

Why random and not standings order: the top of the standings in that rating range is mostly new or
alt accounts (big rating jumps from a low start), which the skip rule rejects, and the few that
pass all had an unusually good day. A seeded shuffle is representative and reproducible.

Writes:
  data/raw/...                 raw snapshots per user (gitignored)
  data/processed/cohort.json   the chosen handles (gitignored)
  cohort_baseline.json         per-tag averages only, no handles (committed; used by the app)

Usage:  python cohort.py [--size 25]
"""

import argparse
import json
import random
from pathlib import Path

import fetch_data
from coach import BASELINE_PATH, load_user
from profiler import build_attempts, cohort_baseline, tag_profile, weak_tags

COHORT_SIZE = 25
RATING_RANGE = (800, 1600)
MIN_CONTESTS = 5
MIN_SOLVED = 50


def recent_div2_contests(k=3):
    contests = fetch_data.fetch("contest.list", {"gym": "false"})  # newest first
    div2 = [
        c
        for c in contests
        if c["phase"] == "FINISHED" and "Div. 2" in c["name"] and "Div. 1" not in c["name"]
    ]
    return div2[:k]


def candidate_handles(contests, seed=0):
    """Participants rated 800-1600 right after one of the contests, shuffled with a fixed seed.

    contest.ratingChanges returns every rated participant with oldRating/newRating in one call, so
    no per-user rating lookups are needed here.
    """
    lo, hi = RATING_RANGE
    handles = set()
    for c in contests:
        for row in fetch_data.fetch("contest.ratingChanges", {"contestId": c["id"]}):
            if lo <= row["newRating"] <= hi:
                handles.add(row["handle"])
    ordered = sorted(handles)  # sets have no stable order; sort first so the seed reproduces
    random.Random(seed).shuffle(ordered)
    return ordered


def passes_skip_rule(handle):
    """Cheap check first (one call), then the full submission history."""
    rating = fetch_data.fetch_rating(handle)
    if len(rating) < MIN_CONTESTS:
        return False, None
    status, _ = load_user(handle)
    attempts = build_attempts(status)
    return int(attempts["solved"].sum()) >= MIN_SOLVED, attempts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--size", type=int, default=COHORT_SIZE)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()

    contests = recent_div2_contests()
    print("contests:", ", ".join(f"{c['id']} {c['name']}" for c in contests))
    candidates = candidate_handles(contests, args.seed)
    print(f"{len(candidates)} participants rated {RATING_RANGE[0]}-{RATING_RANGE[1]}")

    cohort, all_attempts, skipped = [], [], 0
    for handle in candidates:
        ok, attempts = passes_skip_rule(handle)
        if not ok:
            skipped += 1
            print(f"       skip {handle}")
            continue
        cohort.append(handle)
        all_attempts.append(attempts)
        print(f"  [{len(cohort):2d}] kept {handle} ({len(attempts)} problems)")
        if len(cohort) >= args.size:
            break
    print(f"kept {len(cohort)}, skipped {skipped}")

    Path("data/processed").mkdir(parents=True, exist_ok=True)
    Path("data/processed/cohort.json").write_text(json.dumps(cohort, indent=2))

    baseline = cohort_baseline(all_attempts)
    BASELINE_PATH.write_text(json.dumps(baseline, indent=2, sort_keys=True) + "\n")
    print(f"baseline for {len(baseline)} tags -> {BASELINE_PATH.name}")

    # Sanity report: does the profiler say different things about different people?
    print("\nweakest tags per cohort member (vs cohort baseline):")
    for handle, attempts in zip(cohort, all_attempts, strict=True):
        tags = weak_tags(tag_profile(attempts, baseline))["tag"].tolist()
        print(f"  {handle:<20} {', '.join(tags) or '-'}")


if __name__ == "__main__":
    main()
