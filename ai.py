from google import genai
from config import GEMINI_KEY, MAX_HISTORY
from db import get_history

# Initialize Gemini client
client = genai.Client(api_key=GEMINI_KEY)


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
    try:
        prompt = build_prompt(user_id, user_message)

        # IMPORTANT: correct model format for google-genai
        response = client.models.generate_content(
            model="models/gemini-1.5-flash-latest",
            contents=prompt
        )

        if not response or not response.text:
            return "AI returned empty response."

        return response.text.strip()

    except Exception as e:
        print("GEMINI ERROR:", repr(e))
        return "AI service error. Try again later."
