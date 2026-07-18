"""
core/state.py
Session state management for AI Thinking Studio™ Lite.

Handles both local session state (Streamlit) and
Supabase persistence (load/save per expedition).
"""

import streamlit as st


STEPS = [
    "studio_promise",
    "expedition_setup",
    "mirror_room",
    "human_room",
    "possibility_room",
    "battlefield_room",
    "future_room",
    "summary_export",
]

STEP_LABELS = {
    "studio_promise":   "Studio Promise",
    "expedition_setup": "Expedition Setup",
    "mirror_room":      "Mirror Room",
    "human_room":       "Human Room",
    "possibility_room": "Possibility Room",
    "battlefield_room": "Battlefield Room",
    "future_room":      "Future Room",
    "summary_export":   "Expedition Record",
}

STEP_ICONS = {
    "studio_promise":   "◈",
    "expedition_setup": "◎",
    "mirror_room":      "⬡",
    "human_room":       "◉",
    "possibility_room": "◈",
    "battlefield_room": "◆",
    "future_room":      "◇",
    "summary_export":   "■",
}

# All expedition-related state keys (persisted to Supabase)
EXPEDITION_STATE_KEYS = [
    "expedition_setup",
    "mirror_output",
    "human_output",
    "possibility_output",
    "battlefield_output",
    "future_output",
    "revised_challenge",
    "custom_stakeholder",
    "selected_ideas",
    "participant_risk",
    "final_reflection",
]


def _expedition_defaults() -> dict:
    """Return the default values for a fresh expedition."""
    return {
        "expedition_setup": {
            "challenge_title": "",
            "challenge_statement": "",
            "context_background": "",
            "who_is_affected": "",
            "current_consideration": "",
            "hope_to_understand": "",
        },
        "mirror_output":      "",
        "human_output":       "",
        "possibility_output": "",
        "battlefield_output": "",
        "future_output":      "",
        "revised_challenge":  "",
        "custom_stakeholder": "",
        "selected_ideas":     [],
        "participant_risk":   "",
        "final_reflection":   "",
        "mirror_complete":    False,
        "human_complete":     False,
        "possibility_complete": False,
        "battlefield_complete": False,
        "future_complete":    False,
    }


def init_state():
    """
    Initialise all session state keys if not already set.
    Does not touch auth state (managed by auth.py).
    """
    if "current_step" not in st.session_state:
        st.session_state.current_step = "studio_promise"

    defaults = _expedition_defaults()
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def load_expedition_into_state(expedition_data: dict):
    """
    Load expedition data from Supabase into session state.
    Called when a user selects an expedition from the dashboard.
    """
    defaults = _expedition_defaults()
    for key, default in defaults.items():
        st.session_state[key] = expedition_data.get(key, default)
    st.session_state.current_step = "expedition_setup"


def clear_expedition_state():
    """
    Reset all expedition state to defaults.
    Used when starting a new expedition or switching expeditions.
    """
    defaults = _expedition_defaults()
    for key, value in defaults.items():
        st.session_state[key] = value
    st.session_state.current_step = "studio_promise"


def get_current_expedition_state() -> dict:
    """
    Return current expedition state as a flat dict.
    Used for saving to Supabase and generating PDFs.
    """
    return {key: st.session_state.get(key) for key in EXPEDITION_STATE_KEYS}


def navigate_to(step: str):
    """Navigate to a specific step."""
    if step in STEPS:
        st.session_state.current_step = step


def get_expedition_data() -> dict:
    """Return all expedition data in a flat dict for prompt building."""
    setup = st.session_state.expedition_setup
    return {
        "challenge_title":      setup.get("challenge_title", ""),
        "challenge_statement":  setup.get("challenge_statement", ""),
        "context_background":   setup.get("context_background", ""),
        "who_is_affected":      setup.get("who_is_affected", ""),
        "current_consideration":setup.get("current_consideration", ""),
        "hope_to_understand":   setup.get("hope_to_understand", ""),
        "revised_challenge":    st.session_state.get("revised_challenge", ""),
        "custom_stakeholder":   st.session_state.get("custom_stakeholder", ""),
        "selected_ideas":       st.session_state.get("selected_ideas", []),
        "mirror_output":        st.session_state.get("mirror_output", ""),
        "possibility_output":   st.session_state.get("possibility_output", ""),
    }


def is_setup_complete() -> bool:
    """Check if expedition setup has minimum required fields."""
    setup = st.session_state.expedition_setup
    return bool(setup.get("challenge_title") and setup.get("challenge_statement"))


def get_completion_status() -> dict:
    """Return completion status for each step."""
    return {
        "studio_promise":   True,
        "expedition_setup": is_setup_complete(),
        "mirror_room":      bool(st.session_state.get("mirror_output")),
        "human_room":       bool(st.session_state.get("human_output")),
        "possibility_room": bool(st.session_state.get("possibility_output")),
        "battlefield_room": bool(st.session_state.get("battlefield_output")),
        "future_room":      bool(st.session_state.get("future_output")),
        "summary_export":   bool(st.session_state.get("mirror_output")),
    }
