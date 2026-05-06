import streamlit as st
from triage import triage

st.set_page_config(page_title="Bug Triage Bot", page_icon="🐛", layout="wide")

st.title("Bug Report Triage Bot")
st.caption(
    "Paste a bug report. Get instant quality scoring, severity classification, "
    "and routing suggestions powered by Claude."
)

with st.sidebar:
    st.header("How it works")
    st.markdown(
        """
        This tool scores bug reports against a 7-point rubric:
        - Clear title (10pts)
        - Reproduction steps (25pts)
        - Expected vs actual (20pts)
        - Environment details (15pts)
        - Severity indication (10pts)
        - Screenshots/logs (10pts)
        - User impact (10pts)
        """
    )
    st.markdown("---")
    st.markdown("**Tech stack:** Python, Pydantic, Anthropic Claude API, Streamlit")

bug_text = st.text_area(
    "Bug report",
    height=250,
    placeholder="Paste the bug report here...\n\nExample:\nLogin fails with 500 error on Chrome 120 after entering valid credentials...",
)

col_btn, _ = st.columns([1, 5])
with col_btn:
    submit = st.button("Triage", type="primary", disabled=not bug_text.strip())

if submit:
    with st.spinner("Analyzing with Claude..."):
        result = triage(bug_text)

    # Top row: 4 metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Quality Score", f"{result.quality_score}/100")
    c2.metric("Severity", result.severity.upper())
    c3.metric("Category", result.category.title())
    c4.metric("Suggested Owner", result.suggested_owner)

    # Visual quality bar
    st.progress(result.quality_score / 100)

    st.divider()

    # Rewritten title
    st.subheader("Suggested rewrite")
    st.info(result.rewritten_title)

    # Two columns: missing fields + suggestions
    left, right = st.columns(2)

    with left:
        st.subheader("Missing information")
        if result.missing_fields:
            for field in result.missing_fields:
                st.warning(f"- {field}")
        else:
            st.success("Nothing missing — well-formed report.")

    with right:
        st.subheader("Improvement suggestions")
        if result.improvement_suggestions:
            for s in result.improvement_suggestions:
                st.write(f"- {s}")
        else:
            st.write("No suggestions — report is comprehensive.")

    if result.is_likely_duplicate_indicator:
        st.divider()
        st.warning(
            "Vague wording detected — this report may overlap with existing bugs. "
            "Consider searching for similar tickets before filing."
        )

    with st.expander("Raw JSON output"):
        st.json(result.model_dump())