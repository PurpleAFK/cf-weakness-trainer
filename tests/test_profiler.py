import pandas as pd
import pytest

from profiler import (
    build_attempts,
    cohort_baseline,
    rating_band_profile,
    tag_profile,
    target_range,
    weak_tags,
)
from tests.factories import sub


def test_attempts_counts_wrong_only_before_first_ac():
    status = [
        sub(1, "A", "WRONG_ANSWER"),
        sub(1, "A", "TIME_LIMIT_EXCEEDED"),
        sub(1, "A", "OK"),
        sub(1, "A", "WRONG_ANSWER"),  # after AC (e.g. trying a faster solution): not a struggle
    ]
    a = build_attempts(status)
    assert len(a) == 1
    row = a.iloc[0]
    assert row["solved"] and row["wrong"] == 2


def test_unsolved_problem_counts_all_wrong_submits():
    a = build_attempts([sub(2, "B", "WRONG_ANSWER"), sub(2, "B", "WRONG_ANSWER")])
    assert not a.iloc[0]["solved"] and a.iloc[0]["wrong"] == 2


def test_compilation_errors_and_special_tags_are_ignored():
    status = [sub(1, "A", "COMPILATION_ERROR"), sub(1, "A", "OK", tags=("dp", "*special"))]
    a = build_attempts(status)
    assert a.iloc[0]["wrong"] == 0
    assert a.iloc[0]["tags"] == ["dp"]


def test_empty_history():
    a = build_attempts([])
    assert a.empty
    assert tag_profile(a).empty


def _history():
    """greedy: 6 clean solves. dp: 4 problems, 2 unsolved, lots of wrong submits."""
    status = []
    for i in range(6):
        status.append(sub(10 + i, "A", "OK", tags=("greedy",)))
    for i in range(4):
        status.append(sub(20 + i, "B", "WRONG_ANSWER", tags=("dp",)))
        status.append(sub(20 + i, "B", "WRONG_ANSWER", tags=("dp",)))
        if i < 2:
            status.append(sub(20 + i, "B", "OK", tags=("dp",)))
    return build_attempts(status)


def test_struggling_tag_ranks_as_weakest():
    profile = tag_profile(_history())
    assert profile.iloc[0]["tag"] == "dp"
    assert profile.set_index("tag").loc["dp", "weakness"] > 0
    assert profile.set_index("tag").loc["greedy", "weakness"] < 0
    assert list(weak_tags(profile)["tag"]) == ["dp"]


def test_smoothing_keeps_one_failure_from_looking_like_zero_percent():
    status = [sub(i, "A", "OK") for i in range(1, 10)]
    status.append(sub(99, "C", "WRONG_ANSWER", tags=("geometry",)))
    profile = tag_profile(build_attempts(status)).set_index("tag")
    assert profile.loc["geometry", "solve_rate"] > 0.5  # 0/1 raw, pulled toward the 90% average
    assert "geometry" not in set(weak_tags(profile.reset_index())["tag"])  # under MIN_ATTEMPTS


def test_cohort_baseline_changes_the_reference_point():
    a = _history()
    # If peers also fail dp half the time with 2 wrong submits per problem, dp is not a weakness.
    baseline = {"dp": {"rate": 0.5, "wrong": 2.0}, "greedy": {"rate": 1.0, "wrong": 0.0}}
    profile = tag_profile(a, baseline).set_index("tag")
    assert profile.loc["dp", "weakness"] == pytest.approx(0.0, abs=1e-9)


def test_cohort_baseline_needs_three_users():
    users = [_history() for _ in range(3)]
    base = cohort_baseline(users)
    assert base["dp"]["rate"] == pytest.approx(0.5)
    assert cohort_baseline(users[:2]) == {}


def test_rating_bands():
    a = build_attempts(
        [
            sub(1, "A", "OK", rating=800),
            sub(2, "A", "OK", rating=1150),
            sub(3, "A", "WRONG_ANSWER", rating=1199),
        ]
    )
    bands = rating_band_profile(a).set_index("band")
    assert list(bands.index) == [800, 1000]
    assert bands.loc[1000, "solve_rate"] == 0.5


def test_target_range_uses_higher_of_rating_and_recent_solves():
    a = build_attempts([sub(i, "A", "OK", rating=1200) for i in range(5)])
    assert target_range(a, current_rating=900) == (1300, 1500)
    assert target_range(a, current_rating=1450) == (1500, 1700)
    assert target_range(pd.DataFrame(columns=a.columns).astype(a.dtypes)) == (900, 1100)
