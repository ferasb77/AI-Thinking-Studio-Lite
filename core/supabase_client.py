"""
core/supabase_client.py
Supabase connection singleton for AI Thinking Studio™.

Returns a single shared client instance.
Auth state is managed via the client's session methods.
"""

import os
from dotenv import load_dotenv

load_dotenv()

_client = None


def get_supabase():
    """
    Return the shared Supabase client instance.
    Initialises on first call, reuses on subsequent calls.
    """
    global _client

    if _client is not None:
        return _client

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

    _client = create_client(url, key)
    return _client
