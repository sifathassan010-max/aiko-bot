from google import genai
from config import GEMINI_KEY, MAX_HISTORY
from db import get_history

client = genai.Client(api_key=GEMINI_KEY)


def load_character():
    try:
        with open("prompts/character.txt", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "You are a helpful assistant."


def build_prompt(user_id, user_message):
    character = load_character()
    history = get_history(user_id, MAX_HISTORY)

    convo = ""
    for role, content in history:
        convo += f"{role.upper()}: {content}\n"

    return f"""
{character}

Conversation:
{convo}

USER: {user_message}
ASSISTANT:
"""


def generate_reply(user_id, user_message):
    try:
        prompt = build_prompt(user_id, user_message)

        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )

        return response.text.strip()

    except Exception as e:
        print("GEMINI ERROR:", repr(e))
        return f"AI service error: {e}"
