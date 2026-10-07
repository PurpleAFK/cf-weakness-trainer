"""Tiny builders for fake Codeforces API data, so tests don't need network or snapshots."""

import itertools

_clock = itertools.count(1_000_000)


def sub(contest, index, verdict, rating=1000, tags=("greedy",), name=None):
    """One user.status entry. Submits get increasing timestamps in call order."""
    return {
        "creationTimeSeconds": next(_clock),
        "verdict": verdict,
        "problem": {
            "contestId": contest,
            "index": index,
            "name": name or f"P{contest}{index}",
            "rating": rating,
            "tags": list(tags),
        },
    }


def problemset(problems):
    """problemset.problems result from (contest, index, rating, tags, solvedCount) tuples."""
    return {
        "problems": [
            {
                "contestId": c,
                "index": i,
                "name": f"P{c}{i}",
                "type": "PROGRAMMING",
                "rating": r,
                "tags": list(t),
            }
            for c, i, r, t, _ in problems
        ],
        "problemStatistics": [
            {"contestId": c, "index": i, "solvedCount": n} for c, i, _, _, n in problems
        ],
    }
