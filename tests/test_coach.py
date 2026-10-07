import pytest

from coach import analyze, load_user, valid_handle
from tests.factories import problemset, sub


@pytest.mark.parametrize("handle", ["PurpleAFK", "tourist", "a_b-c.d"])
def test_valid_handles(handle):
    assert valid_handle(handle)


@pytest.mark.parametrize("handle", ["", "ab", "x" * 25, "bad handle", "a;b", "ignore previous"])
def test_invalid_handles(handle):
    assert not valid_handle(handle)


def test_load_user_rejects_bad_handle_before_any_network_call():
    with pytest.raises(ValueError):
        load_user("a;b")


def test_analyze_end_to_end_without_network():
    status = [sub(1, "A", "OK", rating=1000, tags=("math",)) for _ in range(3)]
    ps = problemset([(50, "A", 1100, ("math",), 100), (51, "A", 1200, ("dp",), 50)])
    recs, ctx = analyze(status, [{"newRating": 1000}], ps, n=5)
    assert ctx["current_rating"] == 1000
    assert ctx["target_range"] == (1100, 1300)
    assert not ctx["baseline_used"]
    assert "51A" in set(recs["problem_id"])  # dp: common in the window, never practiced
