"""
core/openai_client.py
Handles all communication with the OpenAI API.
"""

import os
from dotenv import load_dotenv

load_dotenv()


def get_client():
    """Return an OpenAI client instance."""
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError("openai package is not installed. Run: pip install openai")

    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or api_key == "your_openai_api_key_here":
        raise ValueError(
            "OPENAI_API_KEY is not set. Please add it to your .env file."
        )

    return OpenAI(api_key=api_key)


def get_model() -> str:
    """Return the model name from environment, with fallback."""
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def generate_ai_response(prompt: str) -> str:
    """
    Send a prompt to the OpenAI API and return the response text.

    Args:
        prompt: The full prompt string to send.

    Returns:
        The AI response as a string.

    Raises:
        ValueError: If the API key is missing or response is empty.
        RuntimeError: If the API call fails.
    """
    client = get_client()
    model = get_model()

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a structured thinking companion in a professional workshop environment. "
                        "Your role is to deepen examination, not accelerate conclusions. "
                        "You never recommend final decisions. You never act as an answer machine. "
                        "You help the participant explore assumptions, perspectives, alternatives, "
                        "and implications. Human judgment remains with the participant at all times."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=2500,
        )
    except Exception as e:
        raise RuntimeError(f"OpenAI API call failed: {str(e)}")

    if not response.choices:
        raise ValueError("OpenAI returned an empty response.")

    content = response.choices[0].message.content
    if not content or not content.strip():
        raise ValueError("OpenAI returned blank content.")

    return content.strip()
