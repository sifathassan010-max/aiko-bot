import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")

MAX_HISTORY = 15
MAX_USERS_PER_MIN = 10  # anti spam
