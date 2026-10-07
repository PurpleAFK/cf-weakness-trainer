"""Streamlit UI. Run:  streamlit run app.py

Streamlit re-runs this whole file top to bottom on every widget change; st.cache_data keeps the slow
API calls from repeating.
"""

import requests
import streamlit as st

import llm
import rag
from coach import analyze, load_baseline, load_problemset, load_user, valid_handle

st.set_page_config(page_title="CF Practice Coach", page_icon="🎯", layout="wide")


@st.cache_data(ttl=3600, show_spinner="Fetching submissions from Codeforces…")
def cached_user(handle):
    return load_user(handle)


@st.cache_data(ttl=24 * 3600, show_spinner="Loading the problemset…")
def cached_problemset():
    return load_problemset()


@st.cache_resource(show_spinner="Loading the notes index…")
def cached_retriever():
    # cache_resource: one shared embedding model per server process, never copied
    return rag.default_retriever()


st.title("🎯 CF Practice Coach")
st.caption(
    "Finds the Codeforces tags you struggle with or rarely practice, "
    "and picks unsolved problems just above your level."
)

with st.sidebar:
    handle = st.text_input("Codeforces handle", value="", placeholder="e.g. PurpleAFK").strip()
    n = st.slider("Problems to recommend", 5, 30, 10)
    use_baseline = st.checkbox(
        "Compare with cohort baseline",
        value=True,
        help="Judge each tag against ~25 peers rated 800-1600 instead of your own average.",
    )

if not handle:
    st.info("Enter a handle in the sidebar to start.")
    st.stop()
if not valid_handle(handle):
    st.error("That doesn't look like a Codeforces handle (3-24 letters, digits, `_`, `-`, `.`).")
    st.stop()

try:
    status, rating = cached_user(handle)
    problemset = cached_problemset()
except (requests.RequestException, RuntimeError) as e:
    st.error(f"Codeforces API error: {e}")
    st.stop()

if not status:
    st.warning(f"{handle} has no submissions yet.")
    st.stop()

baseline = load_baseline() if use_baseline else None
recs, ctx = analyze(status, rating, problemset, n=n, baseline=baseline)
attempts, lo, hi = ctx["attempts"], *ctx["target_range"]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Current rating", ctx["current_rating"] or "unrated")
c2.metric("Problems attempted", len(attempts))
c3.metric("Solved", int(attempts["solved"].sum()))
c4.metric("Practice window", f"{lo}–{hi}")

st.subheader("Coach's notes")
client = llm.client_from_env()
if client is None:
    st.caption(
        "LLM explanations are off. Set `GROQ_API_KEY` (or `LLM_PROVIDER=ollama`/`llamacpp` with a "
        "local server running) to turn them on. Showing the rule-based summary instead."
    )
if st.button("Explain my weak spots", disabled=client is None) or client is None:
    retriever = cached_retriever()
    with st.spinner("Asking the model…"):
        report, meta = llm.explain(ctx, client, retriever)
    titles = {c.id: c.title for c in retriever.store.chunks} if retriever else {}
    st.markdown(f"**{report.summary}**")
    for t in report.tags:
        cite = f"  \n  📚 *{titles.get(t.source, t.source)}*" if t.source else ""
        st.markdown(f"- **{t.tag}**: {t.diagnosis}  \n  💡 {t.hint}{cite}")
    st.markdown(f"**Next step:** {report.next_step}")
    if client is not None:
        label = f"model `{client.model}`" if meta["source"] == "llm" else "rule-based fallback"
        st.caption(f"Source: {label}, {meta['attempts']} attempt(s).")

st.subheader("Recommended problems")
if recs.empty:
    st.write("No unsolved problems match your focus tags in this window.")
else:
    show = recs.assign(tags=recs["tags"].map(", ".join))
    st.dataframe(
        show[["url", "name", "rating", "focus_tag", "reason", "retry", "tags"]],
        column_config={
            "url": st.column_config.LinkColumn("Problem", display_text=r"problem/(\d+/\w+)$"),
            "retry": st.column_config.CheckboxColumn("Retry?"),
        },
        hide_index=True,
        width="stretch",
    )

left, right = st.columns(2)
with left:
    st.subheader("Weak tags")
    ref = "the cohort" if ctx["baseline_used"] else "your average"
    st.caption(f"Weakness > 0 means the tag is harder for you than for {ref}.")
    profile = ctx["profile"]
    enough = profile[profile["attempted"] >= ctx["min_attempts"]]
    st.bar_chart(enough.head(10).set_index("tag")["weakness"], horizontal=True)
    st.dataframe(
        enough[["tag", "attempted", "solved", "solve_rate", "wrong_per_problem", "weakness"]],
        hide_index=True,
        column_config={"solve_rate": st.column_config.NumberColumn(format="percent")},
    )
with right:
    st.subheader("Under-practiced tags")
    st.caption(f"Common in problems rated {lo}–{hi} but rare in your history.")
    under = ctx["underexposed_tags"]
    if under.empty:
        st.write("None: your tag mix matches the window.")
    else:
        st.dataframe(
            under,
            hide_index=True,
            column_config={
                "pool_share": st.column_config.NumberColumn("share in window", format="percent"),
                "user_share": st.column_config.NumberColumn("your share", format="percent"),
            },
        )
    st.subheader("By rating band")
    bands = ctx["bands"]
    st.bar_chart(bands.set_index("band")[["attempted", "solved"]], stack=False)

with st.expander("How this works"):
    st.markdown(
        f"""
- **Attempts:** one row per problem; wrong submits are counted before your first AC
  (compilation errors ignored).
- **Weakness:** `(1 − solve rate) + 0.15 × wrong submits per problem`, minus the same for {ref}.
  Small samples are smoothed with 3 pseudo-attempts at the reference rate.
- **Under-practiced:** tags whose share of your problems is < half their share in the window.
- **Window:** max(rating, median of your last 30 solved) rounded down to 100, then +100…+300.
- **Order:** problems you failed before come first, then a rating ladder, most-solved first.
"""
    )
