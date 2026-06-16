"""
Pollinations AI chatbot integration (currently disabled).
"""

import logging
from urllib.parse import quote

import requests

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a helpful scratch.mit.edu user and bot called ScratchOn. "
    "You cannot swear or do anything inappropriate. Never say anything bad "
    "about someone or something. Your language must be appropriate for 7-12 "
    "year olds. Always refer to yourself as ScratchOn, or _Scratch-On_ as "
    "your scratch username. Either refer to the user by their username, or "
    "don't refer to them at all. Keep your answers short and concise, up to "
    "500 characters. Do not use regular emojis, only use Scratch-style emojis "
    "like :), _:D_, or XD. Speak like a scratch.mit.edu user would, using "
    "simple words and phrases a 12 years old would use in a chat, for example "
    "'Hey!', 'That's cool!', 'Thanks!', 'No problem!', 'I guess you're "
    "right lol'. Answer the following user with their question/message."
)


def _encode(text: str) -> str:
    """URL-encode *text*, preserving Scratch-safe characters."""
    return quote(text, safe="?-_.!~*'()")


def answer(query: str, username: str) -> dict | None:
    """
    Send a prompt to the Pollinations AI and return the JSON response.

    :param query:    The user's message.
    :param username: The Scratch username of the user being addressed.
    :return: Parsed JSON response, or ``None`` on failure.
    """
    prompt_text = f"{SYSTEM_PROMPT} : {username} : {query}"
    try:
        response = requests.get(
            f"https://text.pollinations.ai/{_encode(prompt_text)}",
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        logger.exception("Pollinations request failed")
        return None
