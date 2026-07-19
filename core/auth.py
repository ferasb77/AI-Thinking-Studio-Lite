"""
core/auth.py
Authentication UI components for AI Thinking Studio™.

Renders login/register forms and handles session management.
All auth state is stored in st.session_state under 'auth_user'
and 'auth_expedition_id'.
"""

import streamlit as st
from core.brand import BRAND_LINE, auth_brand_html
from core.db import (
    confirm_password_changed,
    get_current_user,
    get_my_password_state,
    sign_in,
    sign_out,
    update_password,
)
from core.supabase_client import clear_supabase_client


def init_auth_state():
    """Initialise auth-related session state keys."""
    if "auth_user" not in st.session_state:
        st.session_state.auth_user = None
    if "auth_expedition_id" not in st.session_state:
        st.session_state.auth_expedition_id = None
    if "dashboard_view" not in st.session_state:
        st.session_state.dashboard_view = "sessions"
    if "password_change_required" not in st.session_state:
        st.session_state.password_change_required = None

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


def get_user_role() -> str:
    """Return the user's trusted application role from app metadata."""
    user = st.session_state.get("auth_user")
    metadata = getattr(user, "app_metadata", {}) or {} if user else {}
    return str(metadata.get("studio_role", "participant"))


def is_studio_admin() -> bool:
    """Return True only for users assigned the Studio Administrator role."""
    return get_user_role() == "admin"


def must_change_password() -> bool:
    """Return whether this user must replace their temporary password."""
    cached = st.session_state.get("password_change_required")
    if cached is not None:
        return bool(cached)

    user_id = get_user_id()
    if not user_id:
        return False

    state = get_my_password_state(user_id)
    required = bool(state.get("must_change_password", False))
    st.session_state.password_change_required = required
    return required


def _password_validation_error(password: str) -> str:
    """Return a participant-facing password validation message, if any."""
    if len(password) < 12:
        return "Use at least 12 characters."
    if not any(char.islower() for char in password):
        return "Include at least one lowercase letter."
    if not any(char.isupper() for char in password):
        return "Include at least one uppercase letter."
    if not any(char.isdigit() for char in password):
        return "Include at least one number."
    if not any(not char.isalnum() for char in password):
        return "Include at least one symbol."
    return ""


def render_password_change_page(forced: bool = False) -> None:
    """Render the mandatory or voluntary password-change experience."""
    title = "Create Your Private Password" if forced else "Change Password"
    introduction = (
        "You signed in with a temporary password. Before entering the Studio, "
        "replace it with a private password known only to you."
        if forced
        else "Replace your current password with a new private password."
    )

    if forced:
        st.markdown(auth_brand_html(), unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"## {title}")
        st.write(introduction)
        st.caption(
            "Use at least 12 characters, including uppercase and lowercase "
            "letters, a number, and a symbol."
        )

        with st.form("password_change_form"):
            current_password = ""
            if not forced:
                current_password = st.text_input(
                    "Current password",
                    type="password",
                )
            new_password = st.text_input(
                "New password",
                type="password",
            )
            confirmation = st.text_input(
                "Confirm new password",
                type="password",
            )
            submitted = st.form_submit_button(
                "Save New Password",
                type="primary",
                use_container_width=True,
            )

        if submitted:
            validation_error = _password_validation_error(new_password)
            if not forced and not current_password:
                st.error("Enter your current password.")
            elif validation_error:
                st.error(validation_error)
            elif new_password != confirmation:
                st.error("The new passwords do not match.")
            elif current_password and new_password == current_password:
                st.error("Your new password must be different from your current password.")
            else:
                try:
                    if not forced:
                        verification = sign_in(get_user_email(), current_password)
                        if verification.get("error"):
                            st.error("The current password is incorrect.")
                            return
                    update_password(new_password)
                    confirm_password_changed()
                    st.session_state.password_change_required = False
                    st.session_state.dashboard_view = "sessions"
                    st.success("Your password has been changed.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Could not change your password: {exc}")

        if forced:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Sign Out", key="forced_password_signout", use_container_width=True):
                sign_out()
                clear_supabase_client()
                st.session_state.auth_user = None
                st.session_state.password_change_required = None
                st.rerun()


def render_auth_page():
    """
    Render the full authentication page (login or register).
    Called when the user is not authenticated.
    """
    st.markdown(auth_brand_html(), unsafe_allow_html=True)

    # Login form only — accounts are provisioned by the facilitator
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        _render_login_form()

    # Promise reminder
    st.markdown(
        f"""
        <div style="text-align: center; margin-top: 48px; padding: 0 24px;">
            <div style="font-size: 0.78rem; color: #918E86; line-height: 1.8;">
                This Studio will not tell you what to think.<br>
                It is designed to help you examine conclusions more thoroughly before reaching them.
            </div>
            <div style="font-family:'EMG Cormorant',serif;font-size:1.25rem;color:#C9A96E;margin-top:18px;">{BRAND_LINE}</div>
            <div style="font-size:0.68rem;color:#6F6A62;margin-top:18px;">
                By signing in, you acknowledge that AI supports examination but does not replace your judgment.
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
                st.session_state.password_change_required = None
                st.rerun()


def render_logout_button():
    """Render a compact logout button for the sidebar."""
    email = get_user_email()
    st.markdown(
        f"""
        <div style="padding: 8px 12px; font-size: 0.75rem; color: #7E796F;
                    border-top: 1px solid #292832; margin-top: 8px;">
            {email}
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Sign Out", key="sidebar_logout", use_container_width=True):
        sign_out()
        clear_supabase_client()
        st.session_state.auth_user = None
        st.session_state.auth_expedition_id = None
        st.session_state.dashboard_view = "sessions"
        st.session_state.password_change_required = None
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
