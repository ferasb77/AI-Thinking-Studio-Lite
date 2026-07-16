"""
core/auth.py
Authentication UI components for AI Thinking Studio™ Lite.

Renders login/register forms and handles session management.
All auth state is stored in st.session_state under 'auth_user'
and 'auth_expedition_id'.
"""

import streamlit as st
from core.db import sign_in, sign_up, sign_out, get_current_user


def init_auth_state():
    """Initialise auth-related session state keys."""
    if "auth_user" not in st.session_state:
        st.session_state.auth_user = None
    if "auth_expedition_id" not in st.session_state:
        st.session_state.auth_expedition_id = None
    if "auth_view" not in st.session_state:
        st.session_state.auth_view = "login"  # 'login' | 'register'

    # Attempt to restore session from Supabase on first load
    if st.session_state.auth_user is None:
        user = get_current_user()
        if user:
            st.session_state.auth_user = user


def is_authenticated() -> bool:
    """Return True if a user is currently logged in."""
    return st.session_state.get("auth_user") is not None


def get_user_id() -> str:
    """Return the current user's ID, or empty string."""
    user = st.session_state.get("auth_user")
    return str(user.id) if user else ""


def get_user_email() -> str:
    """Return the current user's email, or empty string."""
    user = st.session_state.get("auth_user")
    return str(user.email) if user else ""


def render_auth_page():
    """
    Render the full authentication page (login or register).
    Called when the user is not authenticated.
    """
    st.markdown(
        """
        <div style="max-width: 480px; margin: 40px auto;">
            <div style="text-align: center; margin-bottom: 32px;">
                <div style="font-family: serif; font-size: 1.8rem; color: #A8C4E0;
                            font-weight: 500; margin-bottom: 4px;">
                    AI Thinking Studio™ Lite
                </div>
                <div style="font-size: 0.8rem; color: #3A5A79; letter-spacing: 0.1em;
                            text-transform: uppercase;">
                    A structured thinking environment
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Tab toggle
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        view = st.session_state.auth_view
        tab_login, tab_register = st.tabs(["Sign In", "Create Account"])

        with tab_login:
            _render_login_form()

        with tab_register:
            _render_register_form()

    # Promise reminder
    st.markdown(
        """
        <div style="text-align: center; margin-top: 48px; padding: 0 24px;">
            <div style="font-size: 0.78rem; color: #2A4A6A; font-style: italic; line-height: 1.8;">
                This Studio will not tell you what to think.<br>
                It is designed to help you examine conclusions more thoroughly before reaching them.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_login_form():
    """Render the sign-in form."""
    st.markdown("<br>", unsafe_allow_html=True)

    with st.form("login_form", clear_on_submit=False):
        email = st.text_input(
            "Email",
            placeholder="your@email.com",
            key="login_email",
        )
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Your password",
            key="login_password",
        )
        submitted = st.form_submit_button(
            "Sign In  →",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not email.strip() or not password.strip():
            st.warning("Please enter your email and password.")
        else:
            with st.spinner("Signing in…"):
                result = sign_in(email.strip(), password.strip())
            if result["error"]:
                st.error(result["error"])
            else:
                st.session_state.auth_user = result["user"]
                st.rerun()


def _render_register_form():
    """Render the registration form."""
    st.markdown("<br>", unsafe_allow_html=True)

    with st.form("register_form", clear_on_submit=False):
        email = st.text_input(
            "Email",
            placeholder="your@email.com",
            key="reg_email",
        )
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Choose a password (min. 6 characters)",
            key="reg_password",
        )
        password2 = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Repeat your password",
            key="reg_password2",
        )
        submitted = st.form_submit_button(
            "Create Account  →",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not email.strip():
            st.warning("Please enter your email address.")
        elif len(password) < 6:
            st.warning("Password must be at least 6 characters.")
        elif password != password2:
            st.warning("Passwords do not match.")
        else:
            with st.spinner("Creating your account…"):
                result = sign_up(email.strip(), password.strip())
            if result["error"]:
                st.error(result["error"])
            else:
                st.success(
                    "Account created. You can now sign in."
                )


def render_logout_button():
    """Render a compact logout button for the sidebar."""
    email = get_user_email()
    st.markdown(
        f"""
        <div style="padding: 8px 12px; font-size: 0.75rem; color: #3A5A79;
                    border-top: 1px solid #1A2E45; margin-top: 8px;">
            {email}
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Sign Out", key="sidebar_logout", use_container_width=True):
        sign_out()
        st.session_state.auth_user = None
        st.session_state.auth_expedition_id = None
        # Clear expedition state
        for key in [
            "expedition_setup", "mirror_output", "human_output",
            "possibility_output", "battlefield_output", "future_output",
            "revised_challenge", "custom_stakeholder", "selected_ideas",
            "participant_risk", "final_reflection", "current_step",
        ]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
