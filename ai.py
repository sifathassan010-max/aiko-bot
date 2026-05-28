import google.generativeai as genai
from config import GEMINI_KEY, MAX_HISTORY
from db import get_history
import time

genai.configure(api_key=GEMINI_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")


def load_character():
    try:
        with open("prompts/character.txt", "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return "You are a helpful assistant."


def build_prompt(user_id, user_message):
    character = load_character()
    history = get_history(user_id, MAX_HISTORY)

    convo = ""
    for role, content in history:
        convo += f"{role.upper()}: {content}\n"

    prompt = f"""
{character}

Conversation:
{convo}

USER: {user_message}
ASSISTANT:
"""
    return prompt


def generate_reply(user_id, user_message):
    prompt = build_prompt(user_id, user_message)

    try:
        response = model.generate_content(
            prompt,
            request_options={
                "timeout": 20  # IMPORTANT: prevents hanging
            }
        )

        if not response or not hasattr(response, "text"):
            return "I couldn't generate a response."

        return response.text.strip()

    except Exception as e:
        print(f"[GEMINI ERROR] {e}")
        return "AI service is temporarily unavailable."
