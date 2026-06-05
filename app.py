import streamlit as st

from ui.course_form import render_course_form
from ui.login import render_login
from ui.preview import render_preview
from utils.session import init_session_state

st.set_page_config(
    page_title="Curriculum Structuring System",
    layout="wide",
)

init_session_state()

st.title("📚 Curriculum Structuring System")
st.markdown("---")

if st.session_state.current_step == "preview":
    render_preview()
else:
    render_login()

    if st.session_state.logged_in:
        render_course_form()
