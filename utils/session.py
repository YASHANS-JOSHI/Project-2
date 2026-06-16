import streamlit as st

DEFAULT_STATE = {
    "logged_in": False,
    "username": "",
    "uploaded_file_name": None,
    "program_name": "",
    "course_name": "",
    "credit": 1,
    "level": "UG",
    "model_label": "Standard Model (Academic)",
    "model_type": "standard",
    "generated_result": None,
    "current_step": "form",
    "form_error": None,
    "generation_error": None,
}

MODEL_LABEL_TO_TYPE = {
    "Standard Model (Academic)": "standard",
    "Micro-Unit Model (LMS Style)": "micro",
    "Custom Model (Manual Input)": "custom",
}

MODEL_TYPE_TO_LABEL = {value: key for key, value in MODEL_LABEL_TO_TYPE.items()}


def init_session_state() -> None:
    for key, value in DEFAULT_STATE.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_to_form() -> None:
    st.session_state.current_step = "form"
    st.session_state.generated_result = None
    st.session_state.generation_error = None
    st.session_state.form_error = None
    st.session_state.units_data = None


def store_course_form(
    program_name: str,
    course_name: str,
    credit: int,
    level: str,
    model_label: str,
    uploaded_file_name: str | None,
) -> None:
    st.session_state.program_name = program_name
    st.session_state.course_name = course_name
    st.session_state.credit = credit
    st.session_state.level = level
    st.session_state.model_label = model_label
    st.session_state.model_type = MODEL_LABEL_TO_TYPE.get(model_label, "standard")
    st.session_state.uploaded_file_name = uploaded_file_name
