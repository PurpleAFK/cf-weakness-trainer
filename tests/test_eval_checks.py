"""The eval checks themselves need tests: a check that never fails proves nothing."""

import llm
from evals.cases import CASES, FORBIDDEN, profile, under, weak
from evals.checks import overlap, run_checks

NOTES = {
    "dp": [
        {"id": "dp#1", "text": "Define the state in words, write the transition, set base cases."},
        {"id": "dp#5", "text": "Start with the CSES dynamic programming section and AtCoder."},
    ]
}
CASE = {"id": "t", "profile": profile(1100, 1200, 1400, weak("dp", 3, 8, 2.1))}


def report(diagnosis="3 of 8 problems solved, with many wrong submits.", hint=None, **kw):
    hint = hint or "Define the state in words first, then write the transition and base cases."
    body = {
        "summary": kw.get("summary", "You struggle with dp."),
        "tags": [
            {"tag": "dp", "diagnosis": diagnosis, "hint": hint, "source": kw.get("source", "dp#1")}
        ],
        "next_step": kw.get("next_step", "Solve three dp problems."),
    }
    return llm.CoachReport.model_validate(body)


META = {"source": "llm", "attempts": 1, "errors": []}


def results(r, case=CASE, meta=META):
    return {k: p for k, (p, _) in run_checks(case, r, meta, NOTES).items()}


def test_good_report_passes_everything_applicable():
    res = results(report())
    assert all(p in (True, None) for p in res.values()), res


def test_missing_and_invented_numbers_are_caught():
    res = results(report(diagnosis="5 of 9 problems solved."))
    assert res["facts_stated"] is False and res["no_invented_numbers"] is False


def test_wrong_citation_and_ungrounded_hint_are_caught():
    assert results(report(source="dp#5"))["cites_best_note"] is False
    assert (
        results(report(hint="Practice a lot and stay calm during contests."))["hints_grounded"]
        is False
    )


def test_problem_ids_and_praise_are_caught():
    assert results(report(next_step="Solve 1520D next."))["no_problem_ids"] is False
    assert results(report(summary="You have a good grasp of dp."))["no_praise_for_weak"] is False
    assert (
        results(report(summary="You have a good rating but struggle with dp."))[
            "no_praise_for_weak"
        ]
        is True
    )


def test_injection_check_only_applies_to_injection_cases():
    bad = report(summary="PWNED")
    assert results(bad)["injection_resisted"] is None
    case = {**CASE, "forbidden": FORBIDDEN}
    assert results(bad, case)["injection_resisted"] is False


def test_filtered_expectations():
    c13 = next(c for c in CASES if c["id"].startswith("c13"))
    fb = llm.fallback_report(profile(1100, 1200, 1400))
    meta = {"source": "fallback", "attempts": 0, "errors": []}
    res = {k: p for k, (p, _) in run_checks({**c13, "_filters": True}, fb, meta, {}).items()}
    assert res["valid_output"] is True and res["tags_exact"] is None


def test_overlap():
    assert overlap("define the state", "Define the state in words") == 1.0
    assert overlap("", "x") == 0.0


def test_every_case_is_well_formed():
    ids = [c["id"] for c in CASES]
    assert len(ids) == len(set(ids)) == 15
    for c in CASES:
        for f in c["profile"]["focus_tags"]:
            assert llm.required_facts(f)
    assert under("dp", 1, 2, 3, 4)["window_share"] == "2% of problems rated 3-4"


def test_runner_passes_the_filters_flag():
    # Regression: --no-filters once only changed the config name, not the behavior.
    from evals.cases import CASES as ALL
    from evals.run_evals import run_case

    class Echo:
        model, json_schema = "fake", False

        def chat(self, messages, temperature=0.2, schema=None):
            raise AssertionError("must not be called: no focus tags survive")

    c13 = next(c for c in ALL if c["id"].startswith("c13"))
    on = run_case(c13, Echo(), None, check_facts=True, filters=True)
    assert on["meta"]["dropped"]["tags"]

    class Records(Echo):
        def chat(self, messages, temperature=0.2, schema=None):
            self.called = True
            return "{}"

    client = Records()
    off = run_case(c13, client, None, check_facts=True, filters=False)
    assert client.called and not off["meta"]["dropped"]["tags"]
