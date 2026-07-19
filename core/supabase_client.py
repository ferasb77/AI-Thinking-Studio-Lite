"""
core/supabase_client.py
Supabase connection singleton for AI Thinking Studio™.

Returns a single shared client instance.
Auth state is managed via the client's session methods.
"""

import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def get_supabase():
    """
    Return the shared Supabase client instance.
    Initialises on first call, reuses on subsequent calls.
    """
    # Streamlit module globals are shared across connected browser sessions.
    # Keep the authenticated Supabase client inside the current user's session
    # so one participant's access token can never be reused by another.
    if "_supabase_client" in st.session_state:
        return st.session_state._supabase_client

    try:
        from supabase import create_client
    except ImportError:
        raise RuntimeError(
            "supabase package is not installed. Run: pip install supabase"
        )

    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY", "")

    if not url or url == "https://your-project.supabase.co":
        raise ValueError(
            "SUPABASE_URL is not set. Please add it to your .env file."
        )
    if not key or key == "your_supabase_anon_key_here":
        raise ValueError(
            "SUPABASE_KEY is not set. Please add it to your .env file."
        )

    st.session_state._supabase_client = create_client(url, key)
    return st.session_state._supabase_client


def clear_supabase_client() -> None:
    """Remove the Supabase client associated with the current browser session."""
    st.session_state.pop("_supabase_client", None)
