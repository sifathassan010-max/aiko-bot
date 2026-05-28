import asyncio
import time
from collections import defaultdict

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from db import init_db, save_message
from ai import generate_reply
from images import get_random_image


# -----------------------
# BOT INIT
# -----------------------
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()


# -----------------------
# RATE LIMIT STORAGE
# -----------------------
user_timestamps = defaultdict(list)


def is_rate_limited(user_id: int) -> bool:
    now = time.time()

    # keep only last 60 seconds
    user_timestamps[user_id] = [
        t for t in user_timestamps[user_id] if now - t < 60
    ]

    if len(user_timestamps[user_id]) >= 10:
        return True

    user_timestamps[user_id].append(now)
    return False


# -----------------------
# COMMANDS
# -----------------------
@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Bot is active.")


# -----------------------
# MAIN HANDLER
# -----------------------
@dp.message()
async def handle_message(message: types.Message):
    try:
        user_id = message.from_user.id
        text = message.text

        if not text:
            return

        # RATE LIMIT
        if is_rate_limited(user_id):
            await message.answer("Too many requests. Slow down.")
            return

        # SAVE USER MESSAGE
        save_message(user_id, "user", text)

        # IMAGE TRIGGER
        triggers = ["selfie", "beach", "night", "outdoor"]

        if text.lower() in triggers:
            img = get_random_image(text.lower())
            if img:
                await bot.send_photo(message.chat.id, img)
                return

        # AI RESPONSE
        reply = generate_reply(user_id, text)

        save_message(user_id, "assistant", reply)

        await message.answer(reply)

    except Exception as e:
        # IMPORTANT: prevent silent crash loops
        await message.answer("Bot error occurred. Try again later.")
        print(f"[HANDLER ERROR] {e}")


# -----------------------
# STARTUP
# -----------------------
async def main():
    try:
        # IMPORTANT: avoid webhook conflicts on Railway
        await bot.delete_webhook(drop_pending_updates=True)

        # init DB here (NOT at import time)
        init_db()

        print("Bot started successfully...")

        await dp.start_polling(bot)

    except Exception as e:
        print(f"[FATAL STARTUP ERROR] {e}")
        await asyncio.sleep(5)
        await main()  # safe restart loop


# -----------------------
# ENTRY POINT
# -----------------------
if __name__ == "__main__":
    asyncio.run(main())
