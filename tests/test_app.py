"""Run the Streamlit script headlessly with the network calls replaced by fake data."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import coach
from tests.factories import problemset, sub

APP = str(Path(__file__).resolve().parent.parent / "app.py")


@pytest.fixture
def fake_api(monkeypatch):
    status = [sub(1, "A", "OK", rating=1000, tags=("math",)) for _ in range(5)]
    ps = problemset([(50, "A", 1100, ("math",), 100), (51, "A", 1200, ("dp",), 50)])
    monkeypatch.setattr(coach, "load_user", lambda handle: (status, [{"newRating": 1000}]))
    monkeypatch.setattr(coach, "load_problemset", lambda: ps)


def test_app_asks_for_a_handle():
    at = AppTest.from_file(APP, default_timeout=30).run()
    assert not at.exception
    assert "Enter a handle" in at.info[0].value


def test_app_rejects_bad_handle():
    at = AppTest.from_file(APP, default_timeout=30).run()
    at.sidebar.text_input[0].set_value("drop table;").run()
    assert at.error


def test_app_renders_recommendations(fake_api):
    at = AppTest.from_file(APP, default_timeout=30).run()
    at.sidebar.text_input[0].set_value("someone").run()
    assert not at.exception
    assert at.metric[0].value == "1000"
    assert "Recommended problems" in [s.value for s in at.subheader]
