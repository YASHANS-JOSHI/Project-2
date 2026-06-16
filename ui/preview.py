import html

import streamlit as st

from utils.session import reset_to_form

from services.calculation_engine import calculate_ugc_metrics
from services.time_engine import calculate_time_distribution
from services.slm_generator import generate_slm_structure

PREVIEW_STYLES = """
<style>
.preview-summary-card {
    background: linear-gradient(135deg, #f8f9fc 0%, #eef2f7 100%);
    border: 1px solid #dde3ea;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.06);
}
.preview-summary-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 1rem;
}
.preview-summary-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem 1.5rem;
}
@media (max-width: 768px) {
    .preview-summary-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}
.preview-field-label {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: #64748b;
    margin-bottom: 0.15rem;
}
.preview-field-value {
    font-size: 1rem;
    font-weight: 500;
    color: #0f172a;
    word-break: break-word;
}
.preview-units-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    overflow: hidden;
    font-size: 0.95rem;
    margin-top: 0.5rem;
}
.preview-units-table thead th {
    background: #1e293b;
    color: #f8fafc;
    padding: 0.75rem 1rem;
    text-align: left;
    font-weight: 600;
}
.preview-units-table tbody td {
    padding: 0.65rem 1rem;
    border-bottom: 1px solid #e2e8f0;
}
.preview-units-table tbody tr:last-child td {
    border-bottom: none;
}
.preview-units-table tbody tr:nth-child(even) {
    background: #f8fafc;
}
.preview-units-table tbody tr:hover {
    background: #eef2ff;
}
.preview-badge {
    display: inline-block;
    background: #dbeafe;
    color: #1d4ed8;
    padding: 0.2rem 0.55rem;
    border-radius: 999px;
    font-size: 0.85rem;
    font-weight: 600;
}
.unit-number {
    font-weight: 600;
    color: #0f172a;
    margin-bottom: 0.25rem;
}
.unit-title {
    font-size: 0.9rem;
    font-weight: 500;
    color: #334155;
    margin-top: 0.15rem;
}
.unit-description {
    font-size: 0.85rem;
    color: #64748b;
    line-height: 1.45;
    max-width: 36rem;
}
</style>
"""


def _escape(value: object) -> str:
    return html.escape(str(value))


def _render_html(markup: str) -> None:
    """Render raw HTML without Streamlit's markdown parser rewriting block tags."""
    content = markup.strip()
    if hasattr(st, "html"):
        st.html(content)
    else:
        st.markdown(content, unsafe_allow_html=True)


def _render_summary_card(total_units: int | str, total_topics: int | str) -> None:
    fields = [
        ("Program Name", st.session_state.program_name),
        ("Course Name", st.session_state.course_name),
        ("Credit", st.session_state.credit),
        ("Level", st.session_state.level),
        ("Selected Model", st.session_state.model_label),
        ("Total Units", total_units),
        ("Total Topics", total_topics),
    ]

    grid_items = "".join(
        f'<div><div class="preview-field-label">{_escape(label)}</div>'
        f'<div class="preview-field-value">{_escape(value)}</div></div>'
        for label, value in fields
    )

    _render_html(
        f'<div class="preview-summary-card">'
        f'<div class="preview-summary-title">📋 Syllabus Summary</div>'
        f'<div class="preview-summary-grid">{grid_items}</div>'
        f'</div>'
    )


def _format_topics(topics: list[str]) -> str:
    if not topics:
        return "—"

    return "<br>".join(f"• {_escape(topic)}" for topic in topics)


def _render_units_table(units: list[dict]) -> None:
    rows = "".join(
        f'<tr>'
        f'<td><div class="unit-number">Unit {_escape(unit["unitNumber"])}</div>'
        f'<div class="unit-title">{_escape(unit.get("unitTitle", "—"))}</div></td>'
        f'<td><span class="preview-badge">{_escape(unit["topicCount"])} topics</span></td>'
        f'<td><div class="unit-description">{_format_topics(unit.get("topics", []))}</div></td>'
        f'<td><div class="unit-description">{_escape(unit.get("shortDescription", "—"))}</div></td>'
        f'</tr>'
        for unit in units
    )

    _render_html(
        f'<table class="preview-units-table">'
        f'<thead><tr>'
        f'<th>Unit &amp; Theme</th>'
        f'<th>Topic Count</th>'
        f'<th>Topics</th>'
        f'<th>Description</th>'
        f'</tr></thead>'
        f'<tbody>{rows}</tbody>'
        f'</table>'
    )


def _average_topics_per_unit(units: list[dict]) -> int:
    if not units:
        return 0

    total_topics = sum(unit.get("topicCount", 0) for unit in units)
    return max(1, round(total_topics / len(units))) if total_topics else 0


def render_preview() -> None:
    result = st.session_state.generated_result

    if not result:
        st.warning("No generated structure found. Please complete the course form first.")
        if st.button("Back to Course Form"):
            reset_to_form()
            st.rerun()
        return

    _render_html(PREVIEW_STYLES)

    st.header("Syllabus Structure Preview")
    

    units = result.get("units", [])
    total_units = result.get("totalUnits", len(units) if units else 0)
    total_topics = sum(
        len(unit.get("topics", [])) or unit.get("topicCount", 0)
        for unit in units
    )
    warnings = result.get("warnings", [])
    enforcement = result.get("enforcement", {})

    credit = int(st.session_state.credit)
    topics_per_unit = _average_topics_per_unit(units)

    ugc = calculate_ugc_metrics(
        credit,
        total_units,
        topics_per_unit,
    )

    time_data = calculate_time_distribution(
        total_units,
        topics_per_unit,
        ugc["learning_hours"],
    )

    slm = generate_slm_structure(units)

    if warnings:
        for warning in warnings:
            st.warning(warning)

    if enforcement.get("topicsApplied") and enforcement.get("topicsPreserved"):
        st.success(
            f"Standard Model enforced {total_units} unit(s) with all "
            f"{enforcement.get('totalTopicsExtracted', total_topics)} extracted topic(s) preserved."
        )

    _render_summary_card(total_units, total_topics)

    st.markdown("---")

    st.subheader("UGC / DEB Calculation Engine")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Learning Hours",
            ugc["learning_hours"]
        )

    with col2:
        st.metric(
            "Word Count",
            f'{ugc["min_words"]} - {ugc["max_words"]}'
        )

    with col3:
        st.metric(
            "Pages",
            f'{ugc["min_pages"]} - {ugc["max_pages"]}'
        )

    st.write(
        "Words Per Unit:",
        ugc["words_per_unit"]
    )

    st.write(
        "Words Per Topic:",
        ugc["words_per_topic"]
    )

    st.markdown("---")

    st.subheader("Time & Delivery Engine")

    st.write(
        "Time Per Unit:",
        time_data["time_per_unit"],
        "minutes"
    )

    st.write(
        "Time Per Topic:",
        time_data["time_per_topic"],
        "minutes"
    )

    st.write(
        "Total Course Time:",
        time_data["total_course_time"],
        "minutes"
    )

    st.markdown("---")

    st.subheader("SLM Structure Preview")

    for unit in slm:

        with st.expander(unit["unit_title"]):

            st.write("Introduction:")
            st.write(unit["introduction"])

            st.write("Learning Objectives:")

            for objective in unit["learning_objectives"]:
                st.write("•", objective)

            st.write("Topics:")

            for topic in unit["topics"]:
                st.write("•", topic)

            st.write("Summary:")
            st.write(unit["summary"])

            st.write("Case Study:")
            st.write(unit["case_study"])

    

    st.subheader("Generated Units & Themes")

    st.caption(
        "Standard Model unit count is enforced. Extracted syllabus topics are "
        "redistributed evenly across these units without loss."
    )

    if units:
        _render_units_table(units)
    else:
        st.info("No units were generated.")

    st.markdown("---")

    if st.button("Back to Course Form"):
        reset_to_form()
        st.rerun()
    

