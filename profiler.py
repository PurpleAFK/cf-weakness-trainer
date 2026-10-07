"""Turn a user's raw submissions into a weakness profile.

Pipeline:
    submissions (one row per submit)
      -> attempts (one row per problem: solved?, wrong submits before AC, rating, tags)
      -> tag profile (one row per tag: solve rate, wrong submits, weakness score)
      -> rating-band profile (one row per 200-point band)
"""

import pandas as pd

# Verdicts that say nothing about the solution's logic.
IGNORED_VERDICTS = {"COMPILATION_ERROR", "SKIPPED", "TESTING", None}
# One extra wrong submit costs as much as 15% of an unsolved problem in the difficulty score.
WRONG_WEIGHT = 0.15
# Pseudo-attempts used for smoothing small samples toward the baseline (see tag_profile).
PRIOR_STRENGTH = 3
MIN_ATTEMPTS = 3
# Below this the gap from expected is noise (about one extra wrong submit per 7 problems).
MIN_WEAKNESS = 0.05
BAND_WIDTH = 200


def problem_id(contest_id, index):
    return f"{int(contest_id)}{index}"


def build_attempts(status):
    """One row per problem the user submitted to.

    solved:     at least one OK verdict
    wrong:      non-OK submits before the first OK (or all of them, if never solved)
    """
    rows = []
    for s in status:
        p = s["problem"]
        if "contestId" not in p or s.get("verdict") in IGNORED_VERDICTS:
            continue
        rows.append(
            {
                "problem_id": problem_id(p["contestId"], p["index"]),
                "contest_id": int(p["contestId"]),
                "index": p["index"],
                "name": p.get("name", ""),
                "rating": p.get("rating"),
                "tags": [t for t in p.get("tags", []) if not t.startswith("*")],
                "ok": s["verdict"] == "OK",
                "time": s["creationTimeSeconds"],
            }
        )
    cols = [
        "problem_id",
        "contest_id",
        "index",
        "name",
        "rating",
        "tags",
        "solved",
        "wrong",
        "time",
    ]
    if not rows:
        return pd.DataFrame(columns=cols)

    subs = pd.DataFrame(rows).sort_values("time")
    # Running count of OKs *before* each submit; a submit happened "before the first AC" if it is 0.
    subs["oks_before"] = subs.groupby("problem_id")["ok"].cumsum() - subs["ok"]
    subs["wrong_before_ac"] = (~subs["ok"]) & (subs["oks_before"] == 0)

    attempts = subs.groupby("problem_id", as_index=False).agg(
        contest_id=("contest_id", "first"),
        index=("index", "first"),
        name=("name", "first"),
        rating=("rating", "first"),
        tags=("tags", "first"),
        solved=("ok", "any"),
        wrong=("wrong_before_ac", "sum"),
        time=("time", "max"),  # last activity on this problem
    )
    return attempts[cols]


def _difficulty(rate, wrong_per_problem):
    """How hard problems feel: unsolved share plus a penalty for wrong submits."""
    return (1 - rate) + WRONG_WEIGHT * wrong_per_problem


def tag_profile(attempts, baseline=None):
    """Per-tag stats and a weakness score.

    baseline: optional {tag: {"rate": r, "wrong": w}} from a cohort of similar users. Without it,
    each tag is compared with the user's own overall average.

    Small samples are smoothed toward the baseline with PRIOR_STRENGTH pseudo-attempts: 1 fail out
    of 1 attempt should not look like a 0% solve rate.
    weakness > 0 means "harder for you than expected".
    """
    cols = ["tag", "attempted", "solved", "solve_rate", "wrong_per_problem", "weakness"]
    if attempts.empty:
        return pd.DataFrame(columns=cols)

    overall_rate = attempts["solved"].mean()
    overall_wrong = attempts["wrong"].mean()

    per_tag = (
        attempts.explode("tags")
        .dropna(subset=["tags"])
        .groupby("tags")
        .agg(attempted=("solved", "size"), solved=("solved", "sum"), wrong=("wrong", "sum"))
        .reset_index()
        .rename(columns={"tags": "tag"})
    )

    def base(tag, key, default):
        return baseline.get(tag, {}).get(key, default) if baseline else default

    k = PRIOR_STRENGTH
    exp_rate = per_tag["tag"].map(lambda t: base(t, "rate", overall_rate))
    exp_wrong = per_tag["tag"].map(lambda t: base(t, "wrong", overall_wrong))
    per_tag["solve_rate"] = (per_tag["solved"] + k * exp_rate) / (per_tag["attempted"] + k)
    per_tag["wrong_per_problem"] = (per_tag["wrong"] + k * exp_wrong) / (per_tag["attempted"] + k)
    per_tag["weakness"] = _difficulty(per_tag["solve_rate"], per_tag["wrong_per_problem"]) - (
        _difficulty(exp_rate, exp_wrong)
    )
    per_tag["expected_rate"] = exp_rate
    return per_tag.sort_values("weakness", ascending=False).reset_index(drop=True)


def weak_tags(profile, top_k=3):
    """Tags with enough evidence and a clearly positive weakness score, worst first."""
    enough = profile[(profile["attempted"] >= MIN_ATTEMPTS) & (profile["weakness"] >= MIN_WEAKNESS)]
    return enough.head(top_k)


def rating_band_profile(attempts, width=BAND_WIDTH):
    rated = attempts.dropna(subset=["rating"]).copy()
    rated["band"] = (rated["rating"] // width * width).astype(int)
    bands = rated.groupby("band").agg(
        attempted=("solved", "size"), solved=("solved", "sum"), wrong=("wrong", "mean")
    )
    bands["solve_rate"] = bands["solved"] / bands["attempted"]
    return bands.reset_index()


def target_range(attempts, current_rating=None, recent=30):
    """Practice window just above the user's level.

    level = max(current contest rating, median rating of the last `recent` solved problems),
    rounded down to 100. Practice at level+100 .. level+300, the usual "slightly too hard" zone.
    """
    solved = attempts[attempts["solved"]].dropna(subset=["rating"]).sort_values("time")
    recent_median = solved["rating"].tail(recent).median() if len(solved) else 800
    level = max(current_rating or 0, recent_median, 800)
    level = int(level // 100 * 100)
    return level + 100, level + 300


def cohort_baseline(attempts_by_user):
    """Average per-tag solve rate and wrong submits across a cohort, for tag_profile(baseline=...).

    Each user counts once per tag (mean of user means), so one very active user can't dominate.
    """
    per_user = []
    for attempts in attempts_by_user:
        if attempts.empty:
            continue
        t = attempts.explode("tags").dropna(subset=["tags"]).groupby("tags")
        per_user.append(pd.DataFrame({"rate": t["solved"].mean(), "wrong": t["wrong"].mean()}))
    if not per_user:
        return {}
    stacked = pd.concat(per_user)
    means = stacked.groupby(level=0).mean()
    counts = stacked.groupby(level=0).size()
    means = means[counts >= 3]  # need at least 3 users to trust a tag's baseline
    return {tag: {"rate": float(r.rate), "wrong": float(r.wrong)} for tag, r in means.iterrows()}
