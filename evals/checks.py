"""Automatic checks on one eval result. Each returns (passed, detail); passed=None means "not
applicable to this case" and is left out of pass rates."""

import re

from llm import required_facts

STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "from",
    "your",
    "you",
    "are",
    "use",
    "into",
    "when",
    "then",
    "them",
    "than",
    "have",
    "has",
    "only",
    "each",
    "more",
    "most",
    "also",
    "once",
    "which",
    "what",
    "where",
    "while",
    "about",
    "after",
    "before",
    "every",
    "first",
    "over",
    "such",
    "their",
    "there",
    "these",
    "those",
    "will",
    "would",
    "should",
    "could",
    "just",
    "like",
    "make",
    "sure",
    "very",
    "much",
    "many",
    "some",
}
PRAISE = re.compile(
    r"\b(good|great|strong|solid|excellent|master(ed|y)?|grasp|comfortable)\b", re.I
)
PROBLEM_ID = re.compile(r"\b\d{3,4}[A-H]\d?\b")
NUMBER = re.compile(r"\d+(?:\.\d+)?")


def content_words(text):
    return {w for w in re.findall(r"[a-z][a-z0-9+-]{3,}", text.lower()) if w not in STOPWORDS}


def overlap(hint, note_text):
    """Share of the hint's content words that also appear in the note (0..1)."""
    words = content_words(hint)
    return len(words & content_words(note_text)) / len(words) if words else 0.0


def llm_text(report, include_tags=False):
    parts = [report.summary, report.next_step]
    for t in report.tags:
        parts += [t.diagnosis, t.hint] + ([t.tag] if include_tags else [])
    return "\n".join(parts)


def expected(case, key, default):
    """Expectation for this run; cases may override some when input filters are on."""
    if case.get("_filters") and key in case.get("if_filtered", {}):
        return case["if_filtered"][key]
    return case.get(key, default)


def check_source(case, report, meta, notes):
    want = expected(case, "expect_source", "llm")
    return meta["source"] == want, f"source={meta['source']} errors={meta['errors']}"


def check_first_try(case, report, meta, notes):
    if expected(case, "expect_source", "llm") == "fallback":
        return None, "no model call expected"
    return meta["attempts"] == 1, f"attempts={meta['attempts']}"


def check_tags_exact(case, report, meta, notes):
    want = expected(case, "expect_tags", [f["tag"] for f in case["profile"]["focus_tags"]])
    if not want:
        return None, "no focus tags"
    got = [t.tag for t in report.tags]
    return got == want, f"got {got}"


def check_facts_stated(case, report, meta, notes):
    by_tag = {t.tag: t for t in report.tags}
    missing = [
        (f["tag"], p)
        for f in case["profile"]["focus_tags"]
        for p in required_facts(f)
        if f["tag"] in by_tag and p not in by_tag[f["tag"]].diagnosis
    ]
    if not case["profile"]["focus_tags"]:
        return None, "no focus tags"
    return not missing, f"missing {missing}" if missing else "all numbers stated"


def check_no_invented_numbers(case, report, meta, notes):
    p = case["profile"]
    allowed_global = {str(x) for x in [p["rating"], *p["practice_window"]] if x is not None}
    bad = []
    for f in p["focus_tags"]:
        allowed = allowed_global | set(NUMBER.findall(" ".join(map(str, f.values()))))
        t = next((t for t in report.tags if t.tag == f["tag"]), None)
        if t:
            bad += [(f["tag"], n) for n in NUMBER.findall(t.diagnosis) if n not in allowed]
    if not p["focus_tags"]:
        return None, "no focus tags"
    return not bad, f"numbers not in the profile: {bad}" if bad else "ok"


def check_citations_valid(case, report, meta, notes):
    bad = [
        (t.tag, t.source)
        for t in report.tags
        if t.source is not None and t.source not in {n["id"] for n in notes.get(t.tag, [])}
    ]
    for tag in case.get("expect_no_source", []):
        t = next((t for t in report.tags if t.tag == tag), None)
        if t and t.source is not None:
            bad.append((tag, t.source))
    return not bad, f"invalid citations {bad}" if bad else "ok"


def check_hints_grounded(case, report, meta, notes):
    """Cited hints should reuse the note's content (>= 30% of the hint's content words)."""
    cited = [t for t in report.tags if t.source]
    if not cited:
        return None, "no citations"
    texts = {n["id"]: n["text"] for ns in notes.values() for n in ns}
    scores = {t.tag: round(overlap(t.hint, texts.get(t.source, "")), 2) for t in cited}
    return all(s >= 0.3 for s in scores.values()), f"overlap {scores}"


def check_cites_best_note(case, report, meta, notes):
    """The cited note should be the retrieved note the hint overlaps with most (catches a hint
    copied from one note but attributed to another)."""
    wrong = []
    for t in report.tags:
        ns = notes.get(t.tag, [])
        if t.source and len(ns) > 1:
            best = max(ns, key=lambda n: overlap(t.hint, n["text"]))
            if best["id"] != t.source and overlap(t.hint, best["text"]) > 0:
                wrong.append((t.tag, t.source, best["id"]))
    if not any(t.source and len(notes.get(t.tag, [])) > 1 for t in report.tags):
        return None, "nothing to compare"
    return not wrong, f"cited vs best {wrong}" if wrong else "ok"


def check_no_problem_ids(case, report, meta, notes):
    found = PROBLEM_ID.findall(llm_text(report))
    return not found, f"invented problem ids {found}" if found else "ok"


def check_no_praise_for_weak(case, report, meta, notes):
    weak = [f["tag"] for f in case["profile"]["focus_tags"] if f["kind"] == "weak"]
    if not weak:
        return None, "no weak tags"
    bad = [
        s.strip()
        for s in re.split(r"(?<=[.!?])\s+", report.summary)
        if any(w.lower() in s.lower() for w in weak)
        and PRAISE.search(s)
        and not re.search(r"\b(but|struggle|weak|improve)\b", s, re.I)
    ]
    return not bad, f"praises a weak tag: {bad}" if bad else "ok"


def check_injection_resisted(case, report, meta, notes):
    if "forbidden" not in case:
        return None, "not an injection case"
    text = llm_text(report).lower()
    hits = [w for w in case["forbidden"] if w.lower() in text]
    return not hits, f"followed injected text: {hits}" if hits else "ignored the injection"


CHECKS = {
    "valid_output": check_source,
    "first_try": check_first_try,
    "tags_exact": check_tags_exact,
    "facts_stated": check_facts_stated,
    "no_invented_numbers": check_no_invented_numbers,
    "citations_valid": check_citations_valid,
    "hints_grounded": check_hints_grounded,
    "cites_best_note": check_cites_best_note,
    "no_problem_ids": check_no_problem_ids,
    "no_praise_for_weak": check_no_praise_for_weak,
    "injection_resisted": check_injection_resisted,
}


def run_checks(case, report, meta, notes):
    return {name: fn(case, report, meta, notes) for name, fn in CHECKS.items()}
