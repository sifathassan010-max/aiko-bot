import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from collections import defaultdict
import time

from config import BOT_TOKEN
from db import init_db, save_message
from ai import generate_reply
from images import get_random_image

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

init_db()

# rate limit storage
user_timestamps = defaultdict(list)


def is_rate_limited(user_id):
    now = time.time()

    user_timestamps[user_id] = [
        t for t in user_timestamps[user_id] if now - t < 60
    ]

    if len(user_timestamps[user_id]) >= 10:
        return True

    user_timestamps[user_id].append(now)
    return False


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("Bot is active.")


@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id
    text = message.text

    if not text:
        return

    # RATE LIMIT
    if is_rate_limited(user_id):
        await message.answer("Too many requests. Slow down.")
        return

    # save user message
    save_message(user_id, "user", text)

    # image trigger system
    if text.lower() in ["selfie", "beach", "night", "outdoor"]:
        img = get_random_image(text.lower())

        if img:
            await bot.send_photo(message.chat.id, img)
            return

    # AI response
    try:
        reply = generate_reply(user_id, text)

        save_message(user_id, "assistant", reply)

        await message.answer(reply)

    except Exception as e:
        await message.answer("Error generating response.")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
