"""AI Thinking Studio — an Enable My Growth application."""

import sys
import os

_root = os.path.dirname(os.path.abspath(__file__))
if _root not in sys.path:
    sys.path.insert(0, _root)

import streamlit as st  # ── Auth helpers (app-level) ──────────────────────────────────────────────────

def must_change_password() -> bool:
    user = st.session_state.get("auth_user")
    if not user:
        return False
    try:
        state = get_my_password_state(str(user.id))
        return bool(state.get("must_change_password", False))
    except Exception:
        return False


def is_profile_complete() -> bool:
    user = st.session_state.get("auth_user")
    if not user:
        return False
    try:
        profile = get_my_profile(str(user.id))
        return bool(profile.get("profile_completed_at"))
    except Exception:
        return False


def is_studio_admin() -> bool:
    user = st.session_state.get("auth_user")
    if not user:
        return False
    try:
        meta = getattr(user, "app_metadata", None) or {}
        return meta.get("studio_role") == "admin"
    except Exception:
        return False


def render_password_change_page(forced: bool = False):
    if forced:
        st.markdown(
            """
            <div style="background:#1A0D0D;border:1px solid #4A2A2A;border-radius:8px;
                        padding:20px 24px;margin-bottom:24px;">
                <div style="font-size:0.85rem;color:#E8A0A0;line-height:1.7;">
                    Before entering AI Thinking Studio, please set a new personal password.
                    Your account was provisioned with a temporary password that must be replaced.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<div style=\'font-family:serif;font-size:1.4rem;color:#A8C4E0;margin-bottom:16px;\'>Change Password</div>",
            unsafe_allow_html=True,
        )

    with st.form("change_password_form"):
        new_password     = st.text_input("New Password", type="password",
                                          placeholder="At least 8 characters")
        confirm_password = st.text_input("Confirm New Password", type="password",
                                          placeholder="Repeat your new password")
        submitted = st.form_submit_button(
            "Update Password  →", type="primary", use_container_width=True
        )

    if submitted:
        if len(new_password) < 8:
            st.warning("Password must be at least 8 characters.")
        elif new_password != confirm_password:
            st.warning("Passwords do not match.")
        else:
            try:
                update_password(new_password)
                confirm_password_changed()
                st.success("Password updated. Welcome to AI Thinking Studio.")
                st.rerun()
            except Exception as e:
                st.error(f"Password update failed: {e}")


def render_profile_page(forced: bool = False):
    if forced:
        st.markdown(
            """
            <div style="background:#0D1A0D;border:1px solid #2A4A2A;border-radius:8px;
                        padding:20px 24px;margin-bottom:24px;">
                <div style="font-size:0.85rem;color:#7ECFB0;line-height:1.7;">
                    Please complete your profile before entering the Studio.
                    This information helps the facilitator support your learning journey.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<div style=\'font-family:serif;font-size:1.4rem;color:#A8C4E0;margin-bottom:16px;\'>My Profile</div>",
            unsafe_allow_html=True,
        )

    user_id = get_user_id()
    profile = {}
    try:
        profile = get_my_profile(user_id)
    except Exception:
        pass

    with st.form("profile_form"):
        full_name    = st.text_input("Full Name",
                                      value=profile.get("full_name", "") or "",
                                      placeholder="Your full name")
        phone_number = st.text_input("Phone Number",
                                      value=profile.get("phone_number", "") or "",
                                      placeholder="+9611234567 (include country code)")
        company_name = st.text_input("Company / Organisation",
                                      value=profile.get("company_name", "") or "",
                                      placeholder="Your organisation")
        submitted = st.form_submit_button(
            "Save Profile  →", type="primary", use_container_width=True
        )

    if submitted:
        if not full_name.strip():
            st.warning("Please enter your full name.")
        elif not phone_number.strip():
            st.warning("Please enter your phone number.")
        elif not company_name.strip():
            st.warning("Please enter your company or organisation.")
        else:
            try:
                save_my_profile(user_id, full_name.strip(),
                                phone_number.strip(), company_name.strip())
                st.success("Profile saved.")
                if forced:
                    st.rerun()
                else:
                    st.session_state.dashboard_view = "sessions"
                    st.rerun()
            except Exception as e:
                st.error(f"Could not save profile: {e}")


# noqa: E402

from core.brand import (  # noqa: E402
    BRAND_CSS, BRAND_LINE, ENDORSEMENT, PRODUCT_DESCRIPTOR,
    PRODUCT_EDITION, PRODUCT_NAME, sidebar_brand_html,
)

from core.auth import (  # noqa: E402
    init_auth_state, is_authenticated, get_user_id,
    render_auth_page, render_logout_button,
    detect_invite_token, render_set_password_page,
)

from core.state import (  # noqa: E402
    STEPS, STEP_ICONS, STEP_LABELS,
    init_state, navigate_to, get_expedition_data,
    is_setup_complete, get_completion_status,
    load_expedition_into_state, clear_expedition_state,
    get_current_expedition_state,
)
from core.db import (  # noqa: E402
    get_user_expeditions, create_expedition, delete_expedition,
    save_expedition_field, load_expedition_data, mark_expedition_complete,
    update_expedition_title, get_user_session_stats,
    get_my_password_state, update_password, confirm_password_changed,
    get_my_profile, save_my_profile,
)
from core.prompts import (  # noqa: E402
    build_battlefield_prompt, build_future_prompt, build_human_prompt,
    build_mirror_prompt, build_possibility_prompt,
    build_report_synthesis_prompt,
)
from core.claude_client import generate_ai_response  # noqa: E402
from core.report_builder import generate_pdf  # noqa: E402
from core.toolkit_builder import generate_toolkit_pdf  # noqa: E402

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Thinking Studio™ | Enable My Growth",
    page_icon="◎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown(BRAND_CSS, unsafe_allow_html=True)

# ── Initialise state ───────────────────────────────────────────────────────────
init_auth_state()
init_state()


# ── Auto-save helper ───────────────────────────────────────────────────────────

def autosave(key: str, value):
    """Save a single field to Supabase if an expedition is active."""
    expedition_id = st.session_state.get("auth_expedition_id")
    if expedition_id:
        try:
            save_expedition_field(expedition_id, key, value)
        except Exception:
            pass  # Never block the UI on a save failure


# ── UI helpers ─────────────────────────────────────────────────────────────────

def room_header(icon, title, subtitle, description):
    st.markdown(f"""
        <div style="margin-bottom: 8px;">
            <span style="font-size:1.1rem; color:#918E86; letter-spacing:0.2em;">{icon}</span>
            &nbsp;&nbsp;
            <span class="room-subtitle">{subtitle}</span>
        </div>
        <div class="room-header">{title}</div>
        <div class="room-description">{description}</div>
        <hr class="section-divider">
    """, unsafe_allow_html=True)


def display_ai_output(text: str):
    st.markdown(text)


def run_ai_room(prompt_fn, output_key: str, button_label: str, expedition_data: dict):
    existing = st.session_state.get(output_key, "")
    if existing:
        display_ai_output(existing)
        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    run = st.button(
        button_label if not existing else "↺ Regenerate",
        key=f"btn_{output_key}",
        type="primary" if not existing else "secondary",
    )

    if run:
        if not is_setup_complete():
            st.warning("Please complete the Session Setup before using this room.")
            return False
        with st.spinner("Thinking deeply…"):
            try:
                prompt = prompt_fn(expedition_data)
                result = generate_ai_response(prompt)
                st.session_state[output_key] = result
                autosave(output_key, result)
                st.rerun()
            except ValueError as e:
                st.error(f"Configuration error: {e}")
            except RuntimeError as e:
                st.error(f"AI generation failed: {e}")

    return bool(existing)


# ── Sidebar ────────────────────────────────────────────────────────────────────

def render_sidebar():
    with st.sidebar:
        st.markdown(sidebar_brand_html(), unsafe_allow_html=True)

        for step in STEPS:
            label = STEP_LABELS[step]
            icon  = STEP_ICONS[step]
            if st.button(f"{icon}  {label}", key=f"nav_{step}"):
                navigate_to(step)
                st.rerun()

        # Dashboard link
        st.markdown("<hr style='border:none;border-top:1px solid #292832;margin:16px 12px 8px;'>",
                    unsafe_allow_html=True)
        if st.button("⊞  My Thinking Sessions", key="nav_dashboard"):
            st.session_state.auth_expedition_id = None
            st.session_state.dashboard_view = "sessions"
            clear_expedition_state()
            st.rerun()

        if is_studio_admin():
            if st.button("◉  Studio Overview", key="nav_admin_dashboard"):
                st.session_state.auth_expedition_id = None
                st.session_state.dashboard_view = "admin"
                clear_expedition_state()
                st.rerun()

        if st.button("⌁  Change Password", key="nav_change_password"):
            st.session_state.auth_expedition_id = None
            st.session_state.dashboard_view = "password"
            clear_expedition_state()
            st.rerun()

        if st.button("◇  My Profile", key="nav_profile"):
            st.session_state.auth_expedition_id = None
            st.session_state.dashboard_view = "profile"
            clear_expedition_state()
            st.rerun()

        st.markdown("""
            <hr style="border: none; border-top: 1px solid #292832; margin: 12px 12px;">
            <div style="padding: 0 12px; font-size: 0.72rem; color: #918E86; line-height: 1.6;">
                Human judgment remains<br>with you at all times.
            </div>
            <div style="padding:12px 12px 2px;font-family:'EMG Cormorant',serif;font-size:0.98rem;color:#C9A96E;line-height:1.25;">
                Perspective changes what becomes possible.
            </div>
            <div style="padding:8px 12px 4px;font-size:0.65rem;">
                <a href="https://enablemygrowth.com" target="_blank">enablemygrowth.com</a>
            </div>
        """, unsafe_allow_html=True)

        render_logout_button()


# ── Dashboard ──────────────────────────────────────────────────────────────────

def page_dashboard():
    st.markdown("""
        <div style="margin-bottom: 8px;">
            <div style="font-family: 'EMG Cormorant', serif; font-size: 2rem;
                        color: #EDEAE3; font-weight: 500;">My Thinking Sessions</div>
            <div style="font-size: 0.82rem; color: #918E86; margin-top: 4px;">
                Your structured examinations, saved and ready to continue.
            </div>
        </div>
        <hr class="section-divider">
    """, unsafe_allow_html=True)

    user_id = get_user_id()

    # ── Start new expedition ──
    st.markdown("""
        <div style="font-size: 0.78rem; color: #918E86; text-transform: uppercase;
                    letter-spacing: 0.08em; margin-bottom: 12px;">
            New Thinking Session
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        new_title = st.text_input(
            "Thinking session title",
            placeholder="Give your challenge a working title…",
            label_visibility="collapsed",
            key="new_expedition_title",
        )
    with col2:
        if st.button("Start  →", type="primary", use_container_width=True):
            if not new_title.strip():
                st.warning("Please enter a title for your thinking session.")
            else:
                try:
                    exp = create_expedition(user_id, new_title.strip())
                    st.session_state.auth_expedition_id = exp["id"]
                    st.session_state.dashboard_view = "sessions"
                    clear_expedition_state()
                    # Pre-fill the challenge title
                    st.session_state.expedition_setup["challenge_title"] = new_title.strip()
                    autosave("expedition_setup", st.session_state.expedition_setup)
                    navigate_to("expedition_setup")
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not create the thinking session: {e}")

    # ── Existing expeditions ──
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.markdown("""
        <div style="font-size: 0.78rem; color: #918E86; text-transform: uppercase;
                    letter-spacing: 0.08em; margin-bottom: 12px;">
            Previous Thinking Sessions
        </div>
    """, unsafe_allow_html=True)

    try:
        expeditions = get_user_expeditions(user_id)
    except Exception as e:
        st.error(f"Could not load thinking sessions: {e}")
        return

    if not expeditions:
        st.markdown("""
            <div style="color: #7E796F; font-size: 0.9rem; padding: 20px 0; font-style: italic;">
                No thinking sessions yet. Start one above.
            </div>
        """, unsafe_allow_html=True)
        return

    for exp in expeditions:
        with st.container():
            col1, col2, col3 = st.columns([5, 1, 1])

            status_color = "#C9A96E" if exp["status"] == "complete" else "#C9A96E"
            status_label = "Complete" if exp["status"] == "complete" else "In Progress"

            updated = exp.get("updated_at", "")[:10]

            with col1:
                st.markdown(f"""
                    <div class="expedition-card">
                        <div class="expedition-title">{exp['title']}</div>
                        <div class="expedition-meta">
                            {updated} &nbsp;·&nbsp;
                            <span style="color: {status_color};">{status_label}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

            with col2:
                if st.button("Open", key=f"open_{exp['id']}", use_container_width=True):
                    try:
                        data = load_expedition_data(exp["id"])
                        st.session_state.auth_expedition_id = exp["id"]
                        load_expedition_into_state(data)
                        navigate_to("expedition_setup")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not load the thinking session: {e}")

            with col3:
                if st.button("Delete", key=f"del_{exp['id']}", use_container_width=True):
                    try:
                        delete_expedition(exp["id"])
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not delete: {e}")


def page_admin_dashboard():
    """Render aggregate participation statistics for Studio Administrators."""
    if not is_studio_admin():
        st.error("Studio Administrator access is required.")
        return

    st.markdown("""
        <div style="margin-bottom: 8px;">
            <div style="font-family:'EMG Cormorant',serif;font-size:2rem;
                        color:#EDEAE3;font-weight:500;">Studio Overview</div>
            <div style="font-size:0.82rem;color:#918E86;margin-top:4px;">
                Participation and completion statistics across the Studio.
                Thinking Session content remains private.
            </div>
        </div>
        <hr class="section-divider">
    """, unsafe_allow_html=True)

    try:
        stats = get_user_session_stats()
    except Exception as exc:
        st.error(f"Could not load Studio statistics: {exc}")
        return

    total_users = len(stats)
    total_sessions = sum(int(row.get("total_sessions", 0)) for row in stats)
    completed_sessions = sum(int(row.get("completed_sessions", 0)) for row in stats)
    completion_rate = (
        round((completed_sessions / total_sessions) * 100)
        if total_sessions else 0
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Registered users", total_users)
    col2.metric("Total sessions", total_sessions)
    col3.metric("Completed", completed_sessions)
    col4.metric("Completion rate", f"{completion_rate}%")

    rows = []
    for row in stats:
        completed = int(row.get("completed_sessions", 0))
        total = int(row.get("total_sessions", 0))
        last_completed = row.get("last_completed_at")
        rows.append({
            "Name": row.get("full_name") or "—",
            "Email": row.get("email", ""),
            "Phone": row.get("phone_number") or "—",
            "Company": row.get("company_name") or "—",
            "Completed": completed,
            "In progress": int(row.get("in_progress_sessions", 0)),
            "Total": total,
            "Completion rate": f"{round((completed / total) * 100) if total else 0}%",
            "Last completion": last_completed[:10] if last_completed else "—",
        })

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.dataframe(rows, use_container_width=True, hide_index=True)
    st.caption(
        "A session counts as complete only after all five Thinking Rooms and "
        "the participant's final reflection are completed."
    )


# ── Room pages ─────────────────────────────────────────────────────────────────

def page_studio_promise():
    st.markdown(f"""
        <div class="promise-card">
            <div class="promise-title">{PRODUCT_NAME}</div>
            <div style="font-size: 0.72rem; color: #C9A96E; letter-spacing: 0.16em;
                        text-transform: uppercase; margin-bottom: 24px;">
                {PRODUCT_EDITION}
            </div>
            <div style="font-size: 0.92rem; color: #918E86; margin-bottom: 24px;">{PRODUCT_DESCRIPTOR}</div>
            <hr style="border: none; border-top: 1px solid #292832; margin: 0 0 24px 0;">
            <div style="font-size: 0.8rem; color: #C9A96E; letter-spacing: 0.12em;
                        text-transform: uppercase; margin-bottom: 16px; font-weight: 600;">
                The Studio Promise
            </div>
            <div class="promise-line">This Studio will not tell you what to think.</div>
            <div class="promise-line">It is not designed to help you reach conclusions faster.</div>
            <div class="promise-line" style="color: #EDEAE3; font-weight: 500;">
                It is designed to help you examine conclusions more thoroughly before reaching them.
            </div>
            <div class="promise-line" style="margin-top: 8px;">
                You remain responsible for your judgments, decisions, and actions.
            </div>
            <div style="margin-top: 24px; padding-top: 20px; border-top: 1px solid #292832;">
                <span style="font-family: 'EMG Cormorant', serif; font-size: 1.35rem;
                             color: #C9A96E; font-style: italic;">
                    Better thinking begins before better answers.
                </span>
            </div>
            <div style="margin-top:18px; color:#918E86; font-size:0.72rem; letter-spacing:0.05em;">{ENDORSEMENT}</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="margin: 32px 0 16px 0;">
            <div style="font-size: 0.85rem; color: #918E86; line-height: 1.8;">
                This workshop companion will guide you through a structured
                <strong style="color: #EDEAE3;">Thinking Session</strong> —
                a series of thinking rooms, each designed to examine a different dimension
                of your business challenge before you reach any conclusions.
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("Privacy, data and the role of AI"):
        st.markdown(
            """
            **AI supports examination; it does not make decisions.** Outputs may be incomplete,
            mistaken, or shaped by the information you provide. You remain responsible for how
            the material is interpreted and used.

            Thinking sessions are stored so that you can return to them and prepare your Thinking
            Record. Do not enter confidential, classified, personally identifiable, or commercially
            sensitive information unless you are authorised to process it through this environment.

            You may delete a session from your dashboard. For questions about access, retention,
            or deletion, contact **feras@enablemygrowth.com**.
            """
        )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Go to My Thinking Sessions  →", type="primary", use_container_width=True):
            st.session_state.auth_expedition_id = None
            clear_expedition_state()
            st.rerun()


def page_expedition_setup():
    room_header("01", "Session Setup", "Define your challenge",
        "Before you can examine a problem thoroughly, you must define it with honesty. "
        "The quality of your answers here will shape the quality of every room that follows.")

    setup = st.session_state.expedition_setup

    with st.form("expedition_setup_form"):
        challenge_title = st.text_input(
            "Challenge Title", value=setup.get("challenge_title", ""),
            placeholder="A short, working title for this challenge",
        )
        challenge_statement = st.text_area(
            "Current Challenge Statement", value=setup.get("challenge_statement", ""),
            placeholder="How would you describe the challenge you are facing right now?",
            height=100,
        )
        context_background = st.text_area(
            "Context & Background", value=setup.get("context_background", ""),
            placeholder="What is the broader situation? What led to this challenge?", height=100,
        )
        who_is_affected = st.text_area(
            "Who is Affected?", value=setup.get("who_is_affected", ""),
            placeholder="Which people, teams, or groups have a stake in this?", height=80,
        )
        current_consideration = st.text_area(
            "What Decision, Action, or Solution is Currently Being Considered?",
            value=setup.get("current_consideration", ""),
            placeholder="What direction is already on the table?", height=80,
        )
        hope_to_understand = st.text_area(
            "What Do You Hope to Understand More Clearly?",
            value=setup.get("hope_to_understand", ""),
            placeholder="What specific questions or uncertainties would you like this session to surface?",
            height=80,
        )
        submitted = st.form_submit_button("Save & Begin →", type="primary")

    if submitted:
        if not challenge_title.strip():
            st.warning("Please enter a challenge title.")
        elif not challenge_statement.strip():
            st.warning("Please describe your current challenge statement.")
        else:
            new_setup = {
                "challenge_title":      challenge_title.strip(),
                "challenge_statement":  challenge_statement.strip(),
                "context_background":   context_background.strip(),
                "who_is_affected":      who_is_affected.strip(),
                "current_consideration":current_consideration.strip(),
                "hope_to_understand":   hope_to_understand.strip(),
            }
            st.session_state.expedition_setup = new_setup
            autosave("expedition_setup", new_setup)

            # Keep expedition title in sync
            exp_id = st.session_state.get("auth_expedition_id")
            if exp_id and challenge_title.strip():
                try:
                    update_expedition_title(exp_id, challenge_title.strip())
                except Exception:
                    pass

            st.success("Session setup saved.")
            navigate_to("mirror_room")
            st.rerun()


def page_mirror_room():
    room_header("02", "Mirror Room", "Problem Framing",
        "The Mirror Room reflects your challenge back to you — not as an answer, but as a set of questions. "
        "Before you define the problem, examine how you are defining it. "
        "Assumptions live in the framing. Find them here.")

    if not is_setup_complete():
        st.info("Complete the Session Setup first to use this room.")
        if st.button("Go to Session Setup"):
            navigate_to("expedition_setup")
            st.rerun()
        return

    setup = st.session_state.expedition_setup
    with st.expander("Your current challenge statement", expanded=False):
        st.markdown(f"**{setup['challenge_statement']}**")
        if setup.get("context_background"):
            st.markdown(f"*{setup['context_background']}*")

    expedition_data = get_expedition_data()
    has_output = run_ai_room(
        build_mirror_prompt, "mirror_output",
        "Generate Mirror Room Reflection", expedition_data,
    )

    if has_output:
        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
        st.markdown("""<div style='font-size:0.78rem;color:#918E86;text-transform:uppercase;
                    letter-spacing:0.08em;margin-bottom:8px;'>Your Revised Challenge Statement</div>""",
                    unsafe_allow_html=True)
        st.caption("Review the options above, then write or edit your revised challenge statement below.")

        revised = st.text_area(
            "Revised Challenge Statement",
            value=st.session_state.get("revised_challenge", ""),
            placeholder="Write or paste your chosen revised challenge statement here…",
            height=80, label_visibility="collapsed",
        )
        if st.button("Save Revised Statement", key="save_revised"):
            st.session_state.revised_challenge = revised.strip()
            autosave("revised_challenge", revised.strip())
            st.success("Revised statement saved.")

        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("Next: Human Room →"):
                navigate_to("human_room")
                st.rerun()


def page_human_room():
    room_header("03", "Human Room", "Stakeholder Perspectives",
        "Every challenge involves people whose perspectives you may not yet fully understand. "
        "The Human Room helps you see them more clearly before you engage them.")

    if not is_setup_complete():
        st.info("Complete the Session Setup first.")
        return

    custom = st.text_input(
        "Add a specific stakeholder or group to include (optional)",
        value=st.session_state.get("custom_stakeholder", ""),
        placeholder="e.g. Frontline supervisors, Regional heads, External regulators…",
    )
    if custom != st.session_state.get("custom_stakeholder", ""):
        st.session_state.custom_stakeholder = custom
        autosave("custom_stakeholder", custom)

    expedition_data = get_expedition_data()
    has_output = run_ai_room(
        build_human_prompt, "human_output",
        "Generate Human Room Perspective Map", expedition_data,
    )
    if has_output:
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("Next: Possibility Room →"):
                navigate_to("possibility_room")
                st.rerun()


def page_possibility_room():
    room_header("04", "Possibility Room", "Expanding the Landscape",
        "Before you narrow toward a solution, expand. "
        "The Possibility Room generates a landscape of approaches without declaring any correct. "
        "You will select ideas to carry forward.")

    if not is_setup_complete():
        st.info("Complete the Session Setup first.")
        return

    expedition_data = get_expedition_data()
    has_output = run_ai_room(
        build_possibility_prompt, "possibility_output",
        "Generate Possibility Landscape", expedition_data,
    )

    if has_output:
        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
        st.markdown("""<div style='font-size:0.78rem;color:#918E86;text-transform:uppercase;
                    letter-spacing:0.08em;margin-bottom:8px;'>Select Ideas to Carry Forward</div>""",
                    unsafe_allow_html=True)
        st.caption("Choose 1–3 ideas to stress-test in the Challenge Room.")

        current_ideas = st.session_state.get("selected_ideas", [])
        idea_inputs = []
        for i in range(3):
            val = current_ideas[i] if i < len(current_ideas) else ""
            idea = st.text_input(
                f"Idea {i+1}", value=val,
                placeholder="Describe an approach you want to stress-test…",
                key=f"idea_input_{i}",
            )
            if idea.strip():
                idea_inputs.append(idea.strip())

        if st.button("Save Selected Ideas", key="save_ideas"):
            st.session_state.selected_ideas = idea_inputs
            autosave("selected_ideas", idea_inputs)
            st.success(f"{len(idea_inputs)} idea(s) saved.")

        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("Next: Challenge Room →"):
                navigate_to("battlefield_room")
                st.rerun()


def page_battlefield_room():
    room_header("05", "Challenge Room", "Challenging Selected Ideas",
        "An idea that has not been challenged is not ready. "
        "The Challenge Room stress-tests your selected approaches with firm, constructive skepticism.")

    if not is_setup_complete():
        st.info("Complete the Session Setup first.")
        return

    selected = st.session_state.get("selected_ideas", [])
    if not selected:
        st.info("No ideas selected yet. Return to the Possibility Room to select ideas.")
        if st.button("Go to Possibility Room"):
            navigate_to("possibility_room")
            st.rerun()
        return

    st.markdown("""<div style='font-size:0.78rem;color:#918E86;text-transform:uppercase;
                letter-spacing:0.08em;margin-bottom:8px;'>Ideas Being Challenged</div>""",
                unsafe_allow_html=True)
    for idea in selected:
        st.markdown(
            f"<div style='background:#111118;border-left:2px solid #7A6038;"
            f"padding:8px 16px;margin:4px 0;font-size:0.9rem;color:#D8D3CA;'>{idea}</div>",
            unsafe_allow_html=True,
        )

    # Pre-challenge participant reflection
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.markdown("""
        <div style='background:#111118;border:1px solid #7A6038;border-radius:6px;
                    padding:20px 24px;margin-bottom:20px;'>
            <div style='font-size:0.78rem;color:#C9A96E;text-transform:uppercase;
                        letter-spacing:0.08em;margin-bottom:8px;font-weight:600;'>
                Before the AI Challenge
            </div>
            <div style='font-size:0.9rem;color:#B7B2A8;line-height:1.7;'>
                Before the Studio examines your ideas — what do <em>you</em> think the biggest risk is?
            </div>
        </div>
    """, unsafe_allow_html=True)

    participant_risk = st.text_area(
        "Your biggest concern about these ideas",
        value=st.session_state.get("participant_risk", ""),
        placeholder="What's the risk you're most worried about — before the AI weighs in?",
        height=80, label_visibility="collapsed",
    )
    if participant_risk.strip() != st.session_state.get("participant_risk", ""):
        st.session_state.participant_risk = participant_risk.strip()
        autosave("participant_risk", participant_risk.strip())

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    expedition_data = get_expedition_data()

    def battlefield_with_risk(data):
        return build_battlefield_prompt(
            data, participant_risk=st.session_state.get("participant_risk", "")
        )

    has_output = run_ai_room(
        battlefield_with_risk, "battlefield_output",
        "Generate Challenge Review", expedition_data,
    )
    if has_output:
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("Next: Future Room →"):
                navigate_to("future_room")
                st.rerun()


def page_future_room():
    room_header("06", "Future Room", "Implications & Consequences",
        "If you proceed, what happens next? Across 30 days, 6 months, and 1 year. "
        "Including the consequences you did not intend. "
        "This room does not tell you to proceed or stop. It tells you what to be ready for.")

    if not is_setup_complete():
        st.info("Complete the Session Setup first.")
        return

    expedition_data = get_expedition_data()
    has_output = run_ai_room(
        build_future_prompt, "future_output",
        "Generate Future Room Consequence Map", expedition_data,
    )
    if has_output:
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("Go to Thinking Record →"):
                navigate_to("summary_export")
                st.rerun()


def page_summary_export():
    room_header("07", "Thinking Record", "Review & Export",
        "Your complete Thinking Session — from original framing to future implications — "
        "documented in one place. Review what you've examined. Add your final reflection. Download your record.")

    setup = st.session_state.expedition_setup

    # Challenge overview
    st.markdown("""<div style='font-size:0.78rem;color:#918E86;text-transform:uppercase;
                letter-spacing:0.08em;margin-bottom:12px;'>Your Challenge</div>""",
                unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
            <div style='background:#111118;border:1px solid #292832;border-radius:6px;
                        padding:16px;margin-bottom:12px;'>
                <div style='font-size:0.75rem;color:#C9A96E;text-transform:uppercase;
                            letter-spacing:0.08em;margin-bottom:6px;'>Original Statement</div>
                <div style='font-size:0.9rem;color:#D8D3CA;line-height:1.6;'>
                    {setup.get('challenge_statement','—')}
                </div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        revised = st.session_state.get("revised_challenge", "")
        st.markdown(f"""
            <div style='background:#111118;border:1px solid #7A6038;border-radius:6px;
                        padding:16px;margin-bottom:12px;'>
                <div style='font-size:0.75rem;color:#C9A96E;text-transform:uppercase;
                            letter-spacing:0.08em;margin-bottom:6px;'>Revised Statement</div>
                <div style='font-size:0.9rem;color:#D8D3CA;line-height:1.6;'>
                    {revised if revised else '<span style="color:#7E796F;font-style:italic;">Not yet set</span>'}
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Room completion
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.markdown("""<div style='font-size:0.78rem;color:#918E86;text-transform:uppercase;
                letter-spacing:0.08em;margin-bottom:12px;'>Room Completion</div>""",
                unsafe_allow_html=True)

    status_rooms = [
        ("mirror_output",      "Mirror Room"),
        ("human_output",       "Human Room"),
        ("possibility_output", "Possibility Room"),
        ("battlefield_output", "Challenge Room"),
        ("future_output",      "Future Room"),
    ]
    cols = st.columns(5)
    for i, (key, label) in enumerate(status_rooms):
        done = bool(st.session_state.get(key, ""))
        color = "#C9A96E" if done else "#2A3A4A"
        with cols[i]:
            st.markdown(f"""
                <div style='background:#111118;border:1px solid {color};border-radius:6px;
                            padding:12px;text-align:center;'>
                    <div style='font-size:0.78rem;color:{color};font-weight:500;'>{label}</div>
                    <div style='font-size:0.72rem;color:{color};margin-top:4px;'>
                        {"Complete" if done else "Pending"}
                    </div>
                </div>
            """, unsafe_allow_html=True)

    # Room outputs
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    for key, label in [
        ("mirror_output",      "02 · Mirror Room — Problem Framing"),
        ("human_output",       "03 · Human Room — Stakeholder Perspectives"),
        ("possibility_output", "04 · Possibility Room — Landscape of Approaches"),
        ("battlefield_output", "05 · Challenge Room — Stress Tests"),
        ("future_output",      "06 · Future Room — Consequence Map"),
    ]:
        with st.expander(label, expanded=False):
            content = st.session_state.get(key, "")
            if content:
                st.markdown(content)
            else:
                st.markdown("<span style='color:#7E796F;font-style:italic;'>Not completed.</span>",
                            unsafe_allow_html=True)

    # Selected ideas
    selected = st.session_state.get("selected_ideas", [])
    if selected:
        st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
        st.markdown("""<div style='font-size:0.78rem;color:#918E86;text-transform:uppercase;
                    letter-spacing:0.08em;margin-bottom:8px;'>Selected Ideas</div>""",
                    unsafe_allow_html=True)
        for idea in selected:
            st.markdown(f"<div style='padding:6px 0;color:#D8D3CA;font-size:0.9rem;'>—&nbsp; {idea}</div>",
                        unsafe_allow_html=True)

    # Final reflection
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.markdown("""
        <div style='font-size:0.78rem;color:#918E86;text-transform:uppercase;
                    letter-spacing:0.08em;margin-bottom:4px;'>Final Reflection</div>
        <div style='font-size:0.88rem;color:#C9A96E;margin-bottom:12px;font-style:italic;'>
            What do you now understand more clearly than when you began?
        </div>
    """, unsafe_allow_html=True)

    reflection = st.text_area(
        "Your Final Reflection",
        value=st.session_state.get("final_reflection", ""),
        placeholder="Write your reflection here. There is no right answer. This is your thinking, captured.",
        height=120, label_visibility="collapsed",
    )
    if st.button("Save Reflection", key="save_reflection"):
        st.session_state.final_reflection = reflection.strip()
        autosave("final_reflection", reflection.strip())
        st.success("Reflection saved.")

    required_room_keys = [
        "mirror_output",
        "human_output",
        "possibility_output",
        "battlefield_output",
        "future_output",
    ]
    rooms_ready = all(
        bool(st.session_state.get(key, "").strip()) for key in required_room_keys
    )
    reflection_ready = bool(reflection.strip())
    completion_ready = rooms_ready and reflection_ready

    if not completion_ready:
        st.caption(
            "Complete all five Thinking Rooms and write your final reflection "
            "to finish this Thinking Session."
        )

    if st.button(
        "Complete Thinking Session",
        key="complete_thinking_session",
        type="primary",
        disabled=not completion_ready,
    ):
        exp_id = st.session_state.get("auth_expedition_id")
        if exp_id:
            try:
                st.session_state.final_reflection = reflection.strip()
                save_expedition_field(exp_id, "final_reflection", reflection.strip())
                mark_expedition_complete(exp_id)
                st.success("Thinking Session completed.")
            except Exception as exc:
                st.error(f"Could not complete the Thinking Session: {exc}")

    # ── PDF Export ────────────────────────────────────────────────────────────
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.markdown("""<div style='font-size:0.78rem;color:#918E86;text-transform:uppercase;
                letter-spacing:0.08em;margin-bottom:12px;'>Export Your Thinking Record</div>""",
                unsafe_allow_html=True)

    if not is_setup_complete():
        st.info("Complete the Session Setup to enable PDF export.")
    else:
        if st.button("Prepare PDF Export", key="prepare_pdf"):
            st.session_state.final_reflection = reflection.strip()

            # Build session_data once — used by both synthesis and PDF builder
            session_data = {
                "expedition_setup":  st.session_state.expedition_setup,
                "mirror_output":     st.session_state.get("mirror_output", ""),
                "human_output":      st.session_state.get("human_output", ""),
                "possibility_output":st.session_state.get("possibility_output", ""),
                "battlefield_output":st.session_state.get("battlefield_output", ""),
                "future_output":     st.session_state.get("future_output", ""),
                "revised_challenge": st.session_state.get("revised_challenge", ""),
                "selected_ideas":    st.session_state.get("selected_ideas", []),
                "final_reflection":  st.session_state.get("final_reflection", ""),
                "participant_risk":  st.session_state.get("participant_risk", ""),
            }

            with st.spinner("Generating synthesis — this takes a moment…"):
                try:
                    synthesis_prompt = build_report_synthesis_prompt(session_data)
                    synthesis_text = generate_ai_response(synthesis_prompt)
                    st.session_state["_synthesis_text"] = synthesis_text
                except Exception as e:
                    st.warning(f"Synthesis generation failed — PDF will be generated without it. ({e})")
                    st.session_state["_synthesis_text"] = ""

            with st.spinner("Building PDF…"):
                try:
                    st.session_state["_pdf_bytes"] = generate_pdf(
                        session_data,
                        synthesis_text=st.session_state.get("_synthesis_text", ""),
                    )
                    st.success("PDF ready.")
                except Exception as e:
                    st.error(f"PDF generation failed: {e}")

        if st.session_state.get("_pdf_bytes"):
            from datetime import datetime
            title_slug = (
                st.session_state.expedition_setup
                .get("challenge_title", "export")
                .lower().replace(" ", "-")
            )
            st.download_button(
                label="⬇  Download Thinking Record (PDF)",
                data=st.session_state["_pdf_bytes"],
                file_name=f"ai-thinking-studio-record-{title_slug}-{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
            )

    # ── Toolkit PDF ───────────────────────────────────────────────────────────
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.markdown("""
        <div style='font-size:0.78rem;color:#918E86;text-transform:uppercase;
                    letter-spacing:0.08em;margin-bottom:8px;'>Examination Prompt Toolkit</div>
        <div style='font-size:0.88rem;color:#918E86;margin-bottom:12px;line-height:1.7;'>
            30 examination prompts for use with any AI assistant.
            Use with any AI assistant to deepen examination before decisions are made.
        </div>
    """, unsafe_allow_html=True)

    if st.button("Prepare Prompt Toolkit PDF", key="prepare_toolkit"):
        with st.spinner("Building toolkit…"):
            try:
                st.session_state["_toolkit_bytes"] = generate_toolkit_pdf()
                st.success("Toolkit ready.")
            except Exception as e:
                st.error(f"Toolkit generation failed: {e}")

    if st.session_state.get("_toolkit_bytes"):
        st.download_button(
            label="⬇  Download Examination Prompt Toolkit (PDF)",
            data=st.session_state["_toolkit_bytes"],
            file_name="ai-thinking-studio-examination-prompt-toolkit.pdf",
            mime="application/pdf",
        )


# ── Auth helpers (app-level) ──────────────────────────────────────────────────

def must_change_password() -> bool:
    user = st.session_state.get("auth_user")
    if not user:
        return False
    try:
        state = get_my_password_state(str(user.id))
        return bool(state.get("must_change_password", False))
    except Exception:
        return False


def is_profile_complete() -> bool:
    user = st.session_state.get("auth_user")
    if not user:
        return False
    try:
        profile = get_my_profile(str(user.id))
        return bool(profile.get("profile_completed_at"))
    except Exception:
        return False


def is_studio_admin() -> bool:
    user = st.session_state.get("auth_user")
    if not user:
        return False
    try:
        meta = getattr(user, "app_metadata", None) or {}
        return meta.get("studio_role") == "admin"
    except Exception:
        return False


def render_password_change_page(forced: bool = False):
    if forced:
        st.markdown(
            """
            <div style="background:#1A0D0D;border:1px solid #4A2A2A;border-radius:8px;
                        padding:20px 24px;margin-bottom:24px;">
                <div style="font-size:0.85rem;color:#E8A0A0;line-height:1.7;">
                    Before entering AI Thinking Studio, please set a new personal password.
                    Your account was provisioned with a temporary password that must be replaced.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<div style=\'font-family:serif;font-size:1.4rem;color:#A8C4E0;margin-bottom:16px;\'>Change Password</div>",
            unsafe_allow_html=True,
        )

    with st.form("change_password_form"):
        new_password     = st.text_input("New Password", type="password",
                                          placeholder="At least 8 characters")
        confirm_password = st.text_input("Confirm New Password", type="password",
                                          placeholder="Repeat your new password")
        submitted = st.form_submit_button(
            "Update Password  →", type="primary", use_container_width=True
        )

    if submitted:
        if len(new_password) < 8:
            st.warning("Password must be at least 8 characters.")
        elif new_password != confirm_password:
            st.warning("Passwords do not match.")
        else:
            try:
                update_password(new_password)
                confirm_password_changed()
                st.success("Password updated. Welcome to AI Thinking Studio.")
                st.rerun()
            except Exception as e:
                st.error(f"Password update failed: {e}")


def render_profile_page(forced: bool = False):
    if forced:
        st.markdown(
            """
            <div style="background:#0D1A0D;border:1px solid #2A4A2A;border-radius:8px;
                        padding:20px 24px;margin-bottom:24px;">
                <div style="font-size:0.85rem;color:#7ECFB0;line-height:1.7;">
                    Please complete your profile before entering the Studio.
                    This information helps the facilitator support your learning journey.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<div style=\'font-family:serif;font-size:1.4rem;color:#A8C4E0;margin-bottom:16px;\'>My Profile</div>",
            unsafe_allow_html=True,
        )

    user_id = get_user_id()
    profile = {}
    try:
        profile = get_my_profile(user_id)
    except Exception:
        pass

    with st.form("profile_form"):
        full_name    = st.text_input("Full Name",
                                      value=profile.get("full_name", "") or "",
                                      placeholder="Your full name")
        phone_number = st.text_input("Phone Number",
                                      value=profile.get("phone_number", "") or "",
                                      placeholder="+9611234567 (include country code)")
        company_name = st.text_input("Company / Organisation",
                                      value=profile.get("company_name", "") or "",
                                      placeholder="Your organisation")
        submitted = st.form_submit_button(
            "Save Profile  →", type="primary", use_container_width=True
        )

    if submitted:
        if not full_name.strip():
            st.warning("Please enter your full name.")
        elif not phone_number.strip():
            st.warning("Please enter your phone number.")
        elif not company_name.strip():
            st.warning("Please enter your company or organisation.")
        else:
            try:
                save_my_profile(user_id, full_name.strip(),
                                phone_number.strip(), company_name.strip())
                st.success("Profile saved.")
                if forced:
                    st.rerun()
                else:
                    st.session_state.dashboard_view = "sessions"
                    st.rerun()
            except Exception as e:
                st.error(f"Could not save profile: {e}")


# ── Router ─────────────────────────────────────────────────────────────────────

PAGE_MAP = {
    "studio_promise":   page_studio_promise,
    "expedition_setup": page_expedition_setup,
    "mirror_room":      page_mirror_room,
    "human_room":       page_human_room,
    "possibility_room": page_possibility_room,
    "battlefield_room": page_battlefield_room,
    "future_room":      page_future_room,
    "summary_export":   page_summary_export,
}


def main():
    # ── Auth gate ──────────────────────────────────────────────────────────────
    if not is_authenticated():
        # Check for invite token before showing login
        token_hash, token_type = detect_invite_token()
        if token_hash and token_type in ("invite", "recovery", "email"):
            render_set_password_page(token_hash, token_type)
        else:
            render_auth_page()
        return

    # New participants cannot enter the Studio until the temporary password
    # issued during provisioning has been replaced.
    try:
        password_change_is_required = must_change_password()
    except Exception as exc:
        st.error(f"Could not verify account security status: {exc}")
        return

    if password_change_is_required:
        render_password_change_page(forced=True)
        return

    try:
        profile_is_complete = is_profile_complete()
    except Exception as exc:
        st.error(f"Could not verify profile status: {exc}")
        return

    if not profile_is_complete:
        render_profile_page(forced=True)
        return

    # ── No expedition selected → show dashboard ────────────────────────────────
    if not st.session_state.get("auth_expedition_id"):
        render_sidebar()
        if st.session_state.get("dashboard_view") == "password":
            render_password_change_page(forced=False)
        elif st.session_state.get("dashboard_view") == "profile":
            render_profile_page(forced=False)
        elif (
            st.session_state.get("dashboard_view") == "admin"
            and is_studio_admin()
        ):
            page_admin_dashboard()
        else:
            page_dashboard()
        return

    # ── Expedition active → show rooms ─────────────────────────────────────────
    render_sidebar()
    current  = st.session_state.get("current_step", "studio_promise")
    page_fn  = PAGE_MAP.get(current, page_studio_promise)
    page_fn()


if __name__ == "__main__":
    main()
