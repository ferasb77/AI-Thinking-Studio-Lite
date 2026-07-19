"""
core/db.py
Database access layer for AI Thinking Studio™.

All Supabase read/write operations go through this module.
The rest of the app never imports supabase directly.

Key design:
- Expedition data is stored as key/value pairs in expedition_data table.
- Values are JSONB — strings are stored as JSON strings, dicts as JSON objects.
- All functions return plain Python dicts/lists, never Supabase response objects.
"""

import json
from datetime import datetime, timezone
from typing import Optional
from core.supabase_client import get_supabase


# ── Expedition CRUD ──────────────────────────────────────────────────────────

def create_expedition(user_id: str, title: str) -> dict:
    """
    Create a new expedition for the given user.
    Returns the created expedition row as a dict.
    """
    sb = get_supabase()
    result = (
        sb.table("expeditions")
        .insert({"user_id": user_id, "title": title, "status": "in_progress"})
        .execute()
    )
    return result.data[0]


def get_user_expeditions(user_id: str) -> list:
    """
    Return all expeditions for a user, newest first.
    """
    sb = get_supabase()
    result = (
        sb.table("expeditions")
        .select("*")
        .eq("user_id", user_id)
        .order("updated_at", desc=True)
        .execute()
    )
    return result.data or []


def get_expedition(expedition_id: str) -> Optional[dict]:
    """
    Return a single expedition by ID, or None if not found.
    """
    sb = get_supabase()
    result = (
        sb.table("expeditions")
        .select("*")
        .eq("id", expedition_id)
        .execute()
    )
    return result.data[0] if result.data else None


def update_expedition_title(expedition_id: str, title: str) -> None:
    """Update the title of an expedition."""
    sb = get_supabase()
    sb.table("expeditions").update({"title": title}).eq("id", expedition_id).execute()


def mark_expedition_complete(expedition_id: str) -> None:
    """Mark an expedition complete; database validation enforces readiness."""
    sb = get_supabase()
    sb.table("expeditions").update({"status": "complete"}).eq("id", expedition_id).execute()


def get_user_session_stats() -> list:
    """Return aggregate session statistics for a Studio Administrator."""
    sb = get_supabase()
    result = sb.rpc("get_user_session_stats").execute()
    return result.data or []


def delete_expedition(expedition_id: str) -> None:
    """
    Delete an expedition and all its data (cascade handles data rows).
    """
    sb = get_supabase()
    sb.table("expeditions").delete().eq("id", expedition_id).execute()


# ── Expedition Data ──────────────────────────────────────────────────────────

# Keys used to store expedition fields in expedition_data table.
EXPEDITION_KEYS = [
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


def save_expedition_field(expedition_id: str, key: str, value) -> None:
    """
    Upsert a single field for an expedition.
    value can be a string, list, or dict — stored as JSONB.
    Also touches the expedition's updated_at timestamp.
    """
    sb = get_supabase()

    sb.table("expedition_data").upsert(
        {
            "expedition_id": expedition_id,
            "key": key,
            "value": json.dumps(value),
        },
        on_conflict="expedition_id,key",
    ).execute()

    # Touch the parent expedition's updated_at
    updated_at = datetime.now(timezone.utc).isoformat()
    sb.table("expeditions").update({"updated_at": updated_at}).eq(
        "id", expedition_id
    ).execute()


def load_expedition_data(expedition_id: str) -> dict:
    """
    Load all key/value data for an expedition.
    Returns a flat dict with all stored fields.
    Missing fields return their default empty values.
    """
    sb = get_supabase()
    result = (
        sb.table("expedition_data")
        .select("key, value")
        .eq("expedition_id", expedition_id)
        .execute()
    )

    data = {}
    for row in result.data or []:
        try:
            data[row["key"]] = json.loads(row["value"])
        except (json.JSONDecodeError, TypeError):
            data[row["key"]] = row["value"]

    # Fill in defaults for any missing keys
    defaults = {
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
    }
    for k, v in defaults.items():
        if k not in data:
            data[k] = v

    return data


def save_expedition_snapshot(expedition_id: str, state: dict) -> None:
    """
    Bulk-save all expedition fields from a state dict.
    Used when exporting or completing an expedition.
    """
    for key in EXPEDITION_KEYS:
        if key in state:
            save_expedition_field(expedition_id, key, state[key])


# ── Auth helpers ─────────────────────────────────────────────────────────────

def sign_up(email: str, password: str) -> dict:
    """
    Register a new user.
    Returns {'user': ..., 'error': None} or {'user': None, 'error': str}
    """
    sb = get_supabase()
    try:
        result = sb.auth.sign_up({"email": email, "password": password})
        if result.user:
            return {"user": result.user, "error": None}
        return {"user": None, "error": "Registration failed. Please try again."}
    except Exception as e:
        return {"user": None, "error": str(e)}


def sign_in(email: str, password: str) -> dict:
    """
    Sign in an existing user.
    Returns {'user': ..., 'session': ..., 'error': None} or {'error': str}
    """
    sb = get_supabase()
    try:
        result = sb.auth.sign_in_with_password({"email": email, "password": password})
        if result.user:
            return {"user": result.user, "session": result.session, "error": None}
        return {"user": None, "session": None, "error": "Invalid email or password."}
    except Exception as e:
        msg = str(e)
        if "Invalid login credentials" in msg:
            msg = "Invalid email or password."
        return {"user": None, "session": None, "error": msg}


def sign_out() -> None:
    """Sign out the current user."""
    sb = get_supabase()
    try:
        sb.auth.sign_out()
    except Exception:
        pass


def get_current_user():
    """Return the currently authenticated user, or None."""
    sb = get_supabase()
    try:
        result = sb.auth.get_user()
        return result.user if result else None
    except Exception:
        return None
