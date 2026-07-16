"""
core/claude_client.py
AI provider for AI Thinking Studio™ Lite — Anthropic Claude.

Uses the official Anthropic Python SDK.
Exposes a single function: generate_ai_response(prompt) -> str

Default model: claude-haiku-4-5-20251001 (lowest cost, fast)
Switch model via ANTHROPIC_MODEL env var without changing code.

Architecture note:
    The rest of the app imports only generate_ai_response.
    To swap providers, update the import in app.py to point
    to a different client module (gemini_client, openai_client).
"""

import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = "claude-haiku-4-5-20251001"

SYSTEM_INSTRUCTION = (
    "You are a structured thinking companion in a professional workshop environment. "
    "Your role is to deepen examination, not accelerate conclusions. "
    "You never recommend final decisions. You never act as an answer machine. "
    "You help the participant explore assumptions, perspectives, alternatives, "
    "and implications. Human judgment remains with the participant at all times."
)


def _get_client():
    """Initialise and return an Anthropic client."""
    try:
        import anthropic
    except ImportError:
        raise RuntimeError(
            "anthropic package is not installed. Run: pip install anthropic"
        )

    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key or api_key == "your_anthropic_api_key_here":
        raise ValueError(
            "ANTHROPIC_API_KEY is not set. Please add it to your .env file.\n"
            "Get a key at: https://console.anthropic.com"
        )

    return anthropic.Anthropic(api_key=api_key)


def _get_model() -> str:
    """Return the Claude model name from environment, with fallback."""
    return os.getenv("ANTHROPIC_MODEL", DEFAULT_MODEL)


def generate_ai_response(prompt: str) -> str:
    """
    Send a prompt to the Claude API and return the response text.

    Args:
        prompt: The full prompt string to send.

    Returns:
        The AI response as a string.

    Raises:
        ValueError: If the API key is missing or response is empty.
        RuntimeError: If the API call fails.
    """
    client = _get_client()
    model  = _get_model()

    try:
        response = client.messages.create(
            model=model,
            max_tokens=2500,
            system=SYSTEM_INSTRUCTION,
            messages=[
                {"role": "user", "content": prompt}
            ],
        )
    except Exception as e:
        raise RuntimeError(f"Claude API call failed: {str(e)}")

    if not response.content:
        raise ValueError("Claude returned an empty response.")

    text = response.content[0].text
    if not text or not text.strip():
        raise ValueError("Claude returned blank content.")

    return text.strip()
