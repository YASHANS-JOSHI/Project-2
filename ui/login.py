import streamlit as st


def render_login() -> None:
    st.header("University Login")

    username = st.text_input("Username", value=st.session_state.username)
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        st.session_state.logged_in = True
        st.session_state.username = username
        st.success("Login Successful")
        st.rerun()
