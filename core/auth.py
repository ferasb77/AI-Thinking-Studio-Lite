"""
core/auth.py
Authentication UI for AI Thinking Studio™ Lite.

Handles:
- Login form (email + password)
- Invite token detection and password-set flow
- Session management via Supabase
"""

import streamlit as st
from core.db import sign_in, sign_out, get_current_user


def init_auth_state():
    """Initialise auth-related session state keys."""
    if "auth_user" not in st.session_state:
        st.session_state.auth_user = None
    if "auth_expedition_id" not in st.session_state:
        st.session_state.auth_expedition_id = None

    if st.session_state.auth_user is None:
        user = get_current_user()
        if user:
            st.session_state.auth_user = user


def is_authenticated() -> bool:
    return st.session_state.get("auth_user") is not None


def get_user_id() -> str:
    user = st.session_state.get("auth_user")
    return str(user.id) if user else ""


def get_user_email() -> str:
    user = st.session_state.get("auth_user")
    return str(user.email) if user else ""


def detect_invite_token() -> tuple:
    """
    Check URL query params for a Supabase invite or recovery token.
    Returns (token_hash, token_type) or ("", "").

    Supabase sends invited users to:
    https://studio.enablemygrowth.com/?token_hash=xxx&type=invite
    """
    params = st.query_params
    token_hash = params.get("token_hash", "")
    token_type = params.get("type", "")
    return token_hash, token_type


def render_set_password_page(token_hash: str, token_type: str):
    """
    Render the Set Password page for invited users.
    Called when a valid invite token is detected in the URL.
    """
    st.markdown(
        """
        <div style="text-align: center; margin: 60px auto 32px auto;">
            <div style="font-family: serif; font-size: 1.8rem; color: #A8C4E0;
                        font-weight: 500; margin-bottom: 4px;">
                AI Thinking Studio™ Lite
            </div>
            <div style="font-size: 0.8rem; color: #3A5A79; letter-spacing: 0.1em;
                        text-transform: uppercase;">
                Welcome — set your password to begin
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            """
            <div style="background: #0F1B2D; border: 1px solid #2A4A6E;
                        border-radius: 8px; padding: 28px 32px; margin-bottom: 20px;">
                <div style="font-size: 0.88rem; color: #8899AA; line-height: 1.7;">
                    You have been invited to AI Thinking Studio™ Lite.<br>
                    Choose a password to activate your account.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("set_password_form"):
            password = st.text_input(
                "New Password",
                type="password",
                placeholder="Choose a password (min. 8 characters)",
            )
            password2 = st.text_input(
                "Confirm Password",
                type="password",
                placeholder="Repeat your password",
            )
            submitted = st.form_submit_button(
                "Set Password & Sign In  →",
                type="primary",
                use_container_width=True,
            )

        if submitted:
            if len(password) < 8:
                st.warning("Password must be at least 8 characters.")
            elif password != password2:
                st.warning("Passwords do not match.")
            else:
                with st.spinner("Activating your account…"):
                    result = _verify_token_and_set_password(
                        token_hash, token_type, password
                    )
                if result["error"]:
                    st.error(result["error"])
                else:
                    st.session_state.auth_user = result["user"]
                    st.query_params.clear()
                    st.success("Account activated. Welcome to AI Thinking Studio™.")
                    st.rerun()


def _verify_token_and_set_password(token_hash: str, token_type: str,
                                    new_password: str) -> dict:
    from core.supabase_client import get_supabase
    sb = get_supabase()

    try:
        # Exchange the token for a session
        result = sb.auth.verify_otp({
            "token_hash": token_hash,
            "type": token_type,
        })

        if not result or not result.user:
            return {"user": None, "error": "Invalid or expired invitation link."}

        # Set the password now that we have a valid session
        update_result = sb.auth.update_user({"password": new_password})

        if not update_result or not update_result.user:
            return {"user": None, "error": "Could not set password. Please try again."}

        # The invitation password is the user's first permanent password, so
        # clear the first-login flag immediately after setting it. The RPC uses
        # the authenticated session established by verify_otp() above.
        try:
            from core.db import confirm_password_changed
            confirm_password_changed()
        except Exception:
            pass  # Non-fatal — user can change password on next login if needed

        return {"user": update_result.user, "error": None}

    except Exception as e:
        msg = str(e)
        if "expired" in msg.lower() or "invalid" in msg.lower():
            return {
                "user": None,
                "error": (
                    "This invitation link has expired or already been used. "
                    "Please contact the workshop facilitator for a new invite."
                ),
            }
        return {"user": None, "error": f"Account activation failed: {msg}"}


def render_auth_page():
    """Render the login page."""
    st.markdown(
        """
        <div style="text-align: center; margin: 60px auto 32px auto;">
            <div style="font-family: serif; font-size: 1.8rem; color: #A8C4E0;
                        font-weight: 500; margin-bottom: 4px;">
                AI Thinking Studio™ Lite
            </div>
            <div style="font-size: 0.8rem; color: #3A5A79; letter-spacing: 0.1em;
                        text-transform: uppercase;">
                A structured thinking environment
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        _render_login_form()

    st.markdown(
        """
        <div style="text-align: center; margin-top: 48px; padding: 0 24px;">
            <div style="font-size: 0.78rem; color: #2A4A6A; font-style: italic;
                        line-height: 1.8;">
                This Studio will not tell you what to think.<br>
                It is designed to help you examine conclusions more thoroughly
                before reaching them.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_login_form():
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


def render_logout_button():
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
        for key in [
            "expedition_setup", "mirror_output", "human_output",
            "possibility_output", "battlefield_output", "future_output",
            "revised_challenge", "custom_stakeholder", "selected_ideas",
            "participant_risk", "final_reflection", "current_step",
        ]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
