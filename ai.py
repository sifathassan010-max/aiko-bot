import google.generativeai as genai
from config import GEMINI_KEY, MAX_HISTORY
from db import get_history

# Configure Gemini with API key
genai.configure(api_key=GEMINI_KEY)

# Initialize model
model = genai.GenerativeModel("gemini-1.5-flash")


def load_character():
    try:
        with open("prompt/character.txt", "r", encoding="utf-8") as f:
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
    try:
        prompt = build_prompt(user_id, user_message)

        response = model.generate_content(prompt)

        if not response or not response.text:
            return "AI returned empty response."

        return response.text.strip()

    except Exception as e:
        print("GEMINI ERROR:", repr(e))
        return "AI service error. Try again later."
