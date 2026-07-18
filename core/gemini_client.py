"""
core/gemini_client.py
AI provider for AI Thinking Studio™ — Google Gemini (default).

Uses the official Google Gen AI SDK (google-genai).
Exposes a single function: generate_ai_response(prompt) -> str

Architecture note:
    The rest of the app imports only generate_ai_response from this module.
    To swap providers, update app.py to import from a different client
    (e.g. core/openai_client.py) without touching any room or prompt logic.
"""

import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = "gemini-2.5-flash"

SYSTEM_INSTRUCTION = (
    "You are a structured thinking companion in a professional workshop environment. "
    "Your role is to deepen examination, not accelerate conclusions. "
    "You never recommend final decisions. You never act as an answer machine. "
    "You help the participant explore assumptions, perspectives, alternatives, "
    "and implications. Human judgment remains with the participant at all times."
)


def _get_client():
    """Initialise and return a Google Gen AI client."""
    try:
        import google.genai as genai
    except ImportError:
        raise RuntimeError(
            "google-genai package is not installed. Run: pip install google-genai"
        )

    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key or api_key == "your_gemini_api_key_here":
        raise ValueError(
            "GEMINI_API_KEY is not set. Please add it to your .env file.\n"
            "Get a free key at: https://aistudio.google.com/apikey"
        )

    return genai.Client(api_key=api_key)


def _get_model() -> str:
    """Return the Gemini model name from environment, with fallback."""
    return os.getenv("GEMINI_MODEL", DEFAULT_MODEL)


def generate_ai_response(prompt: str) -> str:
    """
    Send a prompt to the Gemini API and return the response text.

    Args:
        prompt: The full prompt string to send.

    Returns:
        The AI response as a string.

    Raises:
        ValueError: If the API key is missing or the response is empty.
        RuntimeError: If the API call fails.
    """
    import google.genai.types as types

    client = _get_client()
    model = _get_model()

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.7,
                max_output_tokens=2500,
            ),
        )
    except Exception as e:
        raise RuntimeError(f"Gemini API call failed: {str(e)}")

    if not response or not response.text:
        raise ValueError("Gemini returned an empty response.")

    return response.text.strip()
