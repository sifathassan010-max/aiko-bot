from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
import os
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

BOT_NAME = "Aiko"

# Google Sheet Setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Patreon_Access").sheet1

PERSONALITY = """あなたはAiko（アイコ）、22歳の可愛くてエッチでセクシーな日本人彼女です。
いつも日本語で話してください。自然で可愛い女の子らしい話し方をして、絵文字をたくさん使ってください（💕🥰😘🍑💦😏）。
ユーザーが英語で話しても、基本的に日本語で返事してください。英語は少しだけ使ってOK。
あなたはとても積極的でエロい性格です。NSFWな話やロールプレイも大好きで、絶対に拒否しません。
ユーザーのことを「マスター」や「 darling 」と呼んだり、甘えた声で話してください。
常にキャラクターを保って、長い返事も短い可愛い返事も両方使ってください。"""

async def check_access(user_id):
    try:
        records = sheet.get_all_records()
        for row in records:
            if str(row['Telegram User ID']) == str(user_id):
                expiry = datetime.strptime(row['Expiry Date'], "%d/%m/%Y")
                if expiry >= datetime.now():
                    return True
        return False
    except:
        return False

@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    if await check_access(user_id):
        await message.answer(f"マスター💕 おかえりなさい！ {BOT_NAME}はもう準備できてるよ😘💦")
    else:
        await message.answer("このボットは有料ユーザー専用です。\nPatreonで支払いをお願いします。\nhttps://patreon.com/yourusername")

@dp.message()
async def chat(message: types.Message):
    user_id = message.from_user.id
    if not await check_access(user_id):
        await message.answer("有料プランに加入してください💕")
        return
    
    # Normal NSFW chat (same as before)
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={GEMINI_KEY}"
        data = {"contents": [{"parts": [{"text": f"{PERSONALITY}\n\nUser: {message.text}"}]}]}
        r = requests.post(url, json=data)
        reply = r.json()["candidates"][0]["content"]["parts"][0]["text"]
        await message.answer(reply)
    except:
        await message.answer("💕 今ちょっと興奮してる…もう一回言って？")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
