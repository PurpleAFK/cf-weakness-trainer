from profiler import build_attempts
from recommender import problem_pool, recommend, underexposed_tags
from tests.factories import problemset, sub


def _user():
    """Rated ~1000: clean greedy solves, and struggles with dp (2 of 4 unsolved, many WAs)."""
    status = [sub(10 + i, "A", "OK", rating=1000, tags=("greedy",)) for i in range(6)]
    for i in range(4):
        status += [sub(20 + i, "B", "WRONG_ANSWER", rating=1000, tags=("dp",))] * 2
        if i < 2:
            status.append(sub(20 + i, "B", "OK", rating=1000, tags=("dp",)))
    return build_attempts(status)


def _pool():
    return problem_pool(
        problemset(
            [
                (100, "A", 1100, ("dp",), 5000),
                (101, "A", 1200, ("dp",), 4000),
                (102, "A", 1300, ("dp", "greedy"), 3000),
                (103, "A", 1100, ("greedy",), 9000),
                (104, "A", 1100, ("graphs",), 8000),
                (105, "A", 1200, ("graphs",), 7000),
                (106, "A", 2000, ("dp",), 9999),  # too hard: outside the target window
                (10, "A", 1100, ("greedy",), 9999),  # already solved by the user
                (22, "B", 1100, ("dp",), 10),  # tried and failed before -> a retry
            ]
        )
    )


def test_pool_filters_unrated_and_builds_ids():
    ps = problemset([(1, "A", 800, ("math",), 10)])
    ps["problems"].append({"contestId": 2, "index": "A", "type": "PROGRAMMING", "tags": []})
    pool = problem_pool(ps)
    assert list(pool["problem_id"]) == ["1A"]


def test_recommends_weak_tag_inside_target_window_and_skips_solved():
    recs, ctx = recommend(_user(), _pool(), current_rating=1000, n=10)
    assert ctx["target_range"] == (1100, 1300)
    ids = set(recs["problem_id"])
    assert "106A" not in ids  # rating 2000 is outside 1100-1300
    assert "10A" not in ids  # already solved
    assert {"100A", "101A"} <= ids  # dp, the weak tag
    assert (recs["rating"].between(1100, 1300)).all()


def test_failed_problem_comes_first_as_retry():
    recs, _ = recommend(_user(), _pool(), current_rating=1000, n=3)
    assert recs.iloc[0]["problem_id"] == "22B"
    assert recs.iloc[0]["retry"]


def test_underexposed_tag_is_found():
    # graphs is 2 of 6 window problems but the user never tried it.
    under = underexposed_tags(_user(), _pool(), 1100, 1300)
    assert "graphs" in set(under["tag"])
    recs, _ = recommend(_user(), _pool(), current_rating=1000, n=10)
    assert "graphs" in set(recs["focus_tag"])


def test_tags_take_turns_and_no_duplicates():
    recs, _ = recommend(_user(), _pool(), current_rating=1000, n=4)
    assert recs["problem_id"].is_unique
    assert set(recs.head(2)["focus_tag"]) == {"dp", "graphs"}


def test_every_recommendation_has_a_reason_and_link():
    recs, _ = recommend(_user(), _pool(), current_rating=1000)
    assert recs["reason"].str.len().gt(0).all()
    assert recs["url"].str.startswith("https://codeforces.com/problemset/problem/").all()
