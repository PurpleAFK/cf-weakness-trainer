"""Pick unsolved problems in the user's weak and under-practiced tags, just above their level."""

import pandas as pd

from profiler import MIN_ATTEMPTS, problem_id, tag_profile, target_range, weak_tags


def problem_pool(problemset):
    """problemset.problems result -> DataFrame of rated problems with their solve counts."""
    probs = pd.DataFrame(problemset["problems"])
    stats = pd.DataFrame(problemset["problemStatistics"])
    probs = probs.merge(stats, on=["contestId", "index"], how="left")
    probs = probs.dropna(subset=["rating", "contestId"])
    probs = probs[probs["type"] == "PROGRAMMING"] if "type" in probs else probs
    probs["problem_id"] = [
        problem_id(c, i) for c, i in zip(probs["contestId"], probs["index"], strict=True)
    ]
    probs["tags"] = probs["tags"].map(lambda ts: [t for t in ts if not t.startswith("*")])
    probs["rating"] = probs["rating"].astype(int)
    probs["solvedCount"] = probs["solvedCount"].fillna(0).astype(int)
    return probs.reset_index(drop=True)


def underexposed_tags(attempts, pool, lo, hi, top_k=3, min_pool_share=0.05):
    """Tags common in the target rating window that the user has rarely practiced.

    exposure = (user's share of problems with this tag) / (share in the target window).
    A tag with exposure < 0.5 is one the user sees half as often as the contests will show it.
    """
    window = pool[(pool["rating"] >= lo) & (pool["rating"] <= hi)]
    if window.empty or attempts.empty:
        return pd.DataFrame(columns=["tag", "pool_share", "user_share", "exposure"])
    pool_share = window.explode("tags")["tags"].value_counts() / len(window)
    user_share = attempts.explode("tags")["tags"].value_counts() / len(attempts)
    df = pd.DataFrame({"pool_share": pool_share, "user_share": user_share}).fillna(0)
    df = df[df["pool_share"] >= min_pool_share]
    df["exposure"] = df["user_share"] / df["pool_share"]
    df = df[df["exposure"] < 0.5].sort_values("exposure")
    return df.head(top_k).rename_axis("tag").reset_index()


def recommend(attempts, pool, current_rating=None, n=10, baseline=None, top_k=3):
    """Return (recommendations, context).

    Focus tags = top weak tags (struggled with) + top under-practiced tags (rarely tried).
    For each focus tag, candidates are unsolved problems in the target window that carry the tag,
    ordered: problems you already tried and failed first ("retry"), then a rating ladder
    (lo, lo+100, ..., hi, lo, ...) picking the most-solved problem at each rating (popular problems
    tend to be standard and have editorials). Tags take turns (round-robin) so one tag can't fill
    the whole list.
    """
    lo, hi = target_range(attempts, current_rating)
    profile = tag_profile(attempts, baseline)
    weak = weak_tags(profile, top_k)
    under = underexposed_tags(attempts, pool, lo, hi)

    reasons = {}
    for r in weak.itertuples():
        reasons[r.tag] = (
            f"weak: {r.solved}/{r.attempted} solved, "
            f"{r.wrong_per_problem:.1f} wrong submits per problem (smoothed)"
        )
    for r in under.itertuples():
        if r.tag not in reasons:
            reasons[r.tag] = (
                f"under-practiced: {r.user_share:.0%} of your problems vs "
                f"{r.pool_share:.0%} of problems rated {lo}-{hi}"
            )

    solved_ids = set(attempts.loc[attempts["solved"], "problem_id"])
    failed_ids = set(attempts.loc[~attempts["solved"], "problem_id"])
    window = pool[(pool["rating"] >= lo) & (pool["rating"] <= hi)]
    window = window[~window["problem_id"].isin(solved_ids)].copy()
    window["retry"] = window["problem_id"].isin(failed_ids)
    window = window.sort_values("solvedCount", ascending=False)

    queues = {}
    for tag in reasons:
        q = window[window["tags"].map(lambda ts, t=tag: t in ts)].copy()
        q["rung"] = q.groupby("rating").cumcount()  # 0 = most solved at its rating
        queues[tag] = q.sort_values(["retry", "rung", "rating"], ascending=[False, True, True])
    # Round-robin: each tag has its own pointer and skips problems another tag already picked.
    picked, seen = [], set()
    pointers = dict.fromkeys(queues, 0)
    while len(picked) < n and any(pointers[t] < len(q) for t, q in queues.items()):
        for tag, q in queues.items():
            while pointers[tag] < len(q) and q.iloc[pointers[tag]]["problem_id"] in seen:
                pointers[tag] += 1
            if pointers[tag] < len(q) and len(picked) < n:
                row = q.iloc[pointers[tag]]
                seen.add(row["problem_id"])
                picked.append({**row.to_dict(), "focus_tag": tag, "reason": reasons[tag]})
                pointers[tag] += 1

    recs = pd.DataFrame(picked)
    if not recs.empty:
        recs["url"] = [
            f"https://codeforces.com/problemset/problem/{int(c)}/{i}"
            for c, i in zip(recs["contestId"], recs["index"], strict=True)
        ]
        recs = recs[["problem_id", "name", "rating", "tags", "focus_tag", "reason", "retry", "url"]]
    context = {
        "target_range": (lo, hi),
        "profile": profile,
        "weak_tags": weak,
        "underexposed_tags": under,
        "min_attempts": MIN_ATTEMPTS,
    }
    return recs, context
