import streamlit as st
import os

st.set_page_config(
    page_title="Curriculum Structuring System",
    layout="wide"
)

st.title("📚 Curriculum Structuring System")

st.markdown("---")

# University Login
st.header("University Login")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):

    st.success("Login Successful")

    st.markdown("---")

    st.header("Upload Syllabus")

    uploaded_file = st.file_uploader(
        "Upload Syllabus (PDF/DOC)",
        type=["pdf", "doc", "docx"]
    )

    st.markdown("---")

    st.header("Course Details")

    program_name = st.text_input("Program Name")

    course_name = st.text_input("Course Name")

    credit = st.selectbox(
        "Credit",
        [1, 2, 3, 4]
    )

    level = st.selectbox(
        "Level",
        ["UG", "PG"]
    )

    st.markdown("---")

    st.header("Course Structuring Model")

    model = st.radio(
        "Select Model",
        [
            "Standard Model (Academic)",
            "Micro-Unit Model (LMS Style)",
            "Custom Model (Manual Input)"
        ]
    )

    if st.button("Generate Structure"):

        st.success("Information Captured Successfully")

        st.write("### Summary")

        st.write("Program:", program_name)
        st.write("Course:", course_name)
        st.write("Credits:", credit)
        st.write("Level:", level)
        st.write("Selected Model:", model)