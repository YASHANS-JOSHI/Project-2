import streamlit as st

from services.model_service import generate_structure
from services.rule_engine_service import generate_unit_themes, merge_structure_with_themes
from services.validation import validate_course_form
from utils.session import store_course_form


def render_course_form() -> None:
    st.markdown("---")
    st.header("Upload Syllabus")

    uploaded_file = st.file_uploader(
        "Upload Syllabus (PDF/DOC)",
        type=["pdf", "doc", "docx"],
    )

    st.markdown("---")
    st.header("Course Details")

    program_name = st.text_input(
        "Program Name",
        value=st.session_state.program_name,
    )
    course_name = st.text_input(
        "Course Name",
        value=st.session_state.course_name,
    )
    credit = st.selectbox(
        "Credit",
        [1, 2, 3, 4],
        index=[1, 2, 3, 4].index(st.session_state.credit),
    )
    level = st.selectbox(
        "Level",
        ["UG", "PG"],
        index=0 if st.session_state.level == "UG" else 1,
    )

    st.markdown("---")
    st.header("Course Structuring Model")

    model_options = [
        "Standard Model (Academic)",
        "Micro-Unit Model (LMS Style)",
        "Custom Model (Manual Input)",
    ]
    default_model_index = (
        model_options.index(st.session_state.model_label)
        if st.session_state.model_label in model_options
        else 0
    )
    model_label = st.radio(
        "Select Model",
        model_options,
        index=default_model_index,
    )

    if st.session_state.form_error:
        st.error(st.session_state.form_error)

    if st.session_state.generation_error:
        st.error(st.session_state.generation_error)

    if st.button("Proceed to Rule Engine"):
        st.session_state.form_error = None
        st.session_state.generation_error = None

        errors = validate_course_form(
            program_name,
            course_name,
            credit,
            model_label,
        )

        if errors:
            st.session_state.form_error = " ".join(errors)
            st.rerun()

        uploaded_file_name = uploaded_file.name if uploaded_file else None
        store_course_form(
            program_name.strip(),
            course_name.strip(),
            credit,
            level,
            model_label,
            uploaded_file_name,
        )

        with st.spinner("Generating syllabus structure and unit themes..."):
            try:
                result = generate_structure(
                    st.session_state.model_type,
                    st.session_state.credit,
                )
            except RuntimeError as exc:
                st.session_state.generation_error = str(exc)
                st.rerun()

            if result.get("error"):
                st.session_state.generation_error = result["error"]
                st.rerun()

            try:
                themes = generate_unit_themes(
                    st.session_state.course_name,
                    st.session_state.credit,
                    st.session_state.model_type,
                    result["units"],
                )
            except RuntimeError as exc:
                st.session_state.generation_error = str(exc)
                st.rerun()

            if themes.get("error"):
                st.session_state.generation_error = themes["error"]
                st.rerun()

            st.session_state.generated_result = merge_structure_with_themes(
                result,
                themes,
            )
        st.session_state.current_step = "preview"
        st.rerun()
