import html
import os

import streamlit as st

from utils.session import reset_to_form

from services.calculation_engine import calculate_ugc_metrics
from services.time_engine import calculate_time_distribution
from services.slm_generator import generate_slm_structure
from services.unit_ppt_generator import (
    UnitPresentationError,
    generate_unit_presentation,
)
from services.ppt_content_generator import (
    GeminiQuotaExceededError,
    PptContentError,
)
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


def _unit_display_name(unit: dict) -> str:
    return unit.get(
        "unitTitle",
        f"Unit {unit['unitNumber']}",
    )


def _unit_key(unit: dict) -> str:
    return f"unit_{unit.get('unitNumber')}"


def _init_ppt_session_state() -> None:
    if "ppt_files" not in st.session_state:
        st.session_state.ppt_files = {}

    if "ppt_generation_status" not in st.session_state:
        st.session_state.ppt_generation_status = {}

    if "ppt_errors" not in st.session_state:
        st.session_state.ppt_errors = {}

    if "ppt_metadata" not in st.session_state:
        st.session_state.ppt_metadata = {}


def _sync_ppt_state_from_files(units: list[dict]) -> None:
    _init_ppt_session_state()

    for unit in units:
        unit_key = _unit_key(unit)
        ppt_path = st.session_state.ppt_files.get(unit_key)

        if not ppt_path:
            continue

        if os.path.exists(ppt_path):
            st.session_state.ppt_generation_status[unit_key] = "completed"
            st.session_state.ppt_errors.pop(unit_key, None)
            if unit_key not in st.session_state.ppt_metadata:
                _store_ppt_metadata(
                    unit_key,
                    ppt_path,
                    len(unit.get("topics", [])),
                )
        elif (
            st.session_state.ppt_generation_status.get(unit_key)
            == "completed"
        ):
            st.session_state.ppt_generation_status[unit_key] = "failed"
            st.session_state.ppt_errors[unit_key] = (
                "Generated file not found. Please regenerate."
            )


def _ppt_slide_count(ppt_path: str) -> int | None:
    try:
        from pptx import Presentation

        return len(Presentation(ppt_path).slides)
    except Exception:
        return None


def _store_ppt_metadata(
    unit_key: str,
    ppt_path: str,
    topic_count: int,
) -> None:
    slide_count = _ppt_slide_count(ppt_path)
    st.session_state.ppt_metadata[unit_key] = {
        "slides": slide_count,
        "topics": topic_count,
        "filename": os.path.basename(ppt_path),
    }


def _generate_unit_ppt(
    unit: dict,
    unit_index: int,
    total_units: int,
    ugc: dict,
    *,
    force: bool = False,
) -> str:
    _init_ppt_session_state()

    unit_key = _unit_key(unit)
    unit_name = _unit_display_name(unit)
    unit_number = unit.get("unitNumber", unit_index)
    topics = unit.get("topics", [])

    if not force:
        existing_path = st.session_state.ppt_files.get(unit_key)
        status = st.session_state.ppt_generation_status.get(
            unit_key,
            "not_started",
        )
        if (
            status == "completed"
            and existing_path
            and os.path.exists(existing_path)
        ):
            return "skipped"

    st.session_state.ppt_generation_status[unit_key] = "generating"
    status_box = st.empty()
    status_box.info(
        f"Generating Unit {unit_index} of {total_units}: {unit_name}"
    )

    try:
        ppt_path = generate_unit_presentation(
            unit_name=unit_name,
            topics=topics,
            words_per_unit=ugc["words_per_unit"],
            words_per_topic=ugc["words_per_topic"],
            unit_number=unit_number,
            course_name=st.session_state.course_name,
            academic_level=st.session_state.level,
        )
        st.session_state.ppt_files[unit_key] = ppt_path
        st.session_state.ppt_generation_status[unit_key] = "completed"
        st.session_state.ppt_errors.pop(unit_key, None)
        _store_ppt_metadata(unit_key, ppt_path, len(topics))
        status_box.success(f"Completed Unit {unit_number}: {unit_name}")
        return "success"
    except GeminiQuotaExceededError as error:
        st.session_state.ppt_generation_status[unit_key] = "failed"
        st.session_state.ppt_errors[unit_key] = str(error)
        status_box.error(str(error))
        return "quota"
    except (PptContentError, UnitPresentationError) as error:
        st.session_state.ppt_generation_status[unit_key] = "failed"
        st.session_state.ppt_errors[unit_key] = str(error)
        status_box.error(f"Unit {unit_number}: {error}")
        return "failed"
    except Exception as error:
        st.session_state.ppt_generation_status[unit_key] = "failed"
        st.session_state.ppt_errors[unit_key] = str(error)
        status_box.error(f"Unit {unit_number}: {error}")
        return "failed"


def _render_unit_download(unit_key: str) -> None:
    ppt_path = st.session_state.ppt_files.get(unit_key)

    if not ppt_path:
        return

    if not os.path.exists(ppt_path):
        st.warning("Generated file not found. Please regenerate.")
        return

    with open(ppt_path, "rb") as ppt_file:
        st.download_button(
            label="📥 Download PPT",
            data=ppt_file.read(),
            file_name=os.path.basename(ppt_path),
            mime=(
                "application/vnd.openxmlformats-officedocument"
                ".presentationml.presentation"
            ),
            key=f"download_{unit_key}",
        )


def _render_unit_ppt_status(unit: dict) -> None:
    unit_key = _unit_key(unit)
    unit_name = _unit_display_name(unit)
    unit_number = unit.get("unitNumber")
    topic_count = len(unit.get("topics", []))
    status = st.session_state.ppt_generation_status.get(
        unit_key,
        "not_started",
    )
    metadata = st.session_state.ppt_metadata.get(unit_key, {})
    ppt_path = st.session_state.ppt_files.get(unit_key)

    st.markdown(f"### Unit {unit_number}: {unit_name}")

    if status == "completed" and ppt_path and os.path.exists(ppt_path):
        st.success("✅ Completed")
        slides_generated = metadata.get("slides")
        if slides_generated is not None:
            st.write(f"Slides Generated: {slides_generated}")
        st.write(f"Topics Covered: {metadata.get('topics', topic_count)}")
        st.write(
            "Generated File: "
            f"{metadata.get('filename', os.path.basename(ppt_path))}"
        )
        _render_unit_download(unit_key)
    elif status == "completed" and (
        not ppt_path or not os.path.exists(ppt_path)
    ):
        st.warning("Generated file not found. Please regenerate.")
    elif status == "generating":
        st.info("Generating...")
    elif status == "failed":
        error_message = st.session_state.ppt_errors.get(unit_key)
        if error_message:
            st.error(error_message)
    else:
        st.caption(f"{topic_count} topics — Not started")


def _render_ppt_generation(units: list[dict], ugc: dict) -> None:
    _init_ppt_session_state()
    _sync_ppt_state_from_files(units)
    total_units = len(units)

    st.markdown("---")
    st.subheader("PowerPoint Generation")
    st.caption(
        "One Gemini API call per unit. UGC/DEB word budgets guide depth only: "
        f"{ugc['words_per_unit']} words/unit and "
        f"{ugc['words_per_topic']} words/topic (average), "
        f"within {ugc['min_words']}–{ugc['max_words']} total words."
    )

    action_col, clear_col = st.columns(2)

    with action_col:
        generate_all = st.button(
            "Generate All Unit PPTs",
            type="primary",
            key="generate_all_ppts",
        )

    with clear_col:
        if st.button("Clear Generated PPTs", key="clear_generated_ppts"):
            st.session_state.ppt_files = {}
            st.session_state.ppt_generation_status = {}
            st.session_state.ppt_errors = {}
            st.session_state.ppt_metadata = {}
            st.rerun()

    if generate_all:
        progress = st.progress(0.0)
        status = st.empty()

        for index, unit in enumerate(units, start=1):
            unit_name = _unit_display_name(unit)
            status.write(
                f"Generating Unit {index} of {total_units}: {unit_name}"
            )
            result = _generate_unit_ppt(
                unit,
                index,
                total_units,
                ugc,
            )
            progress.progress(index / total_units)

            if result == "quota":
                st.error(
                    "Gemini quota or rate limit reached. "
                    "Completed units remain available for download."
                )
                break

        completed = sum(
            1
            for unit in units
            if st.session_state.ppt_generation_status.get(
                _unit_key(unit)
            ) == "completed"
            and os.path.exists(
                st.session_state.ppt_files.get(_unit_key(unit), "")
            )
        )
        if completed:
            st.success(
                f"Generated {completed} of {total_units} unit presentation(s)."
            )

    for index, unit in enumerate(units, start=1):
        unit_number = unit.get("unitNumber", index)

        with st.container(border=True):
            if st.button(
                "Generate Unit PPT",
                key=f"generate_ppt_{unit_number}",
            ):
                _generate_unit_ppt(
                    unit,
                    index,
                    total_units,
                    ugc,
                    force=True,
                )

            _render_unit_ppt_status(unit)

    if st.session_state.ppt_errors:
        st.subheader("Generation Errors")

        for unit in units:
            unit_key = _unit_key(unit)
            message = st.session_state.ppt_errors.get(unit_key)
            if message:
                st.error(f"{_unit_display_name(unit)}: {message}")


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

    _render_ppt_generation(units, ugc)

    st.markdown("---")
    if st.button("Back to Course Form"):
        reset_to_form()
        st.rerun()
    

