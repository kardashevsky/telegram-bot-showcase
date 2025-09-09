from dotenv import load_dotenv
import os, time, json, asyncio
import httpx
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

INVITE_TEXT = (
    "Привет! Это инвайт в GENZA — первый геймифицированный дейтинг в Telegram.\n\n"
    "Здесь AI соединяет людей по вайбу и ценностям, а не только по фото.\n\n"
    "Переходи по моей ссылке — получишь 1000 монет, а я — бонус 🚀"
)

# ── ENV ─────────────────────────────────────────────────────────────────────────
load_dotenv()
BOT_TOKEN = os.environ["BOT_TOKEN"]
WEBAPP_URL = os.environ["WEBAPP_URL"]   # t.me/<bot>?startapp=...
PHOTO_URL  = os.environ["PHOTO_URL"]    # https://.../image.jpg
API_URL    = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ── BOT / HTTP APP ──────────────────────────────────────────────────────────────
bot = Bot(BOT_TOKEN)
dp = Dispatcher()
app = FastAPI()

# ── PREPARED MESSAGE (RAW Bot API) ─────────────────────────────────────────────
async def create_prepared_message(user_id: int, photo_url: str, caption: str) -> dict:
    result = {
        "type": "photo",
        "id": str(int(time.time() * 1000)),
        "photo_url": photo_url,
        "thumb_url": photo_url,   # важно: thumb_url (не thumbnail_url)
        "title": "GENZA",
        "caption": caption,
    }
    payload = {
        "user_id": user_id,
        "result": result,
        "allow_user_chats": True,
        "allow_group_chats": True,
        "allow_channel_chats": False,
        "allow_bot_chats": False,
    }
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(f"{API_URL}/savePreparedInlineMessage", json=payload)
        if r.status_code != 200:
            raise RuntimeError(f"savePreparedInlineMessage failed: {r.status_code} {r.text}")
        return r.json()["result"]  # {"id": "...", "expiration_date": ...}

# ── /start → фото + кнопка + message_id в подписи (HTML) ───────────────────────
@dp.message(CommandStart())
async def on_start(m):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Open Mini App", url=WEBAPP_URL)]]
    )
    pim = await create_prepared_message(m.from_user.id, PHOTO_URL, "Готовая заготовка ✨")
    caption = INVITE_TEXT
    await m.answer_photo(photo=PHOTO_URL, caption=caption, reply_markup=kb, parse_mode="HTML")

# ── HTTP API: подготовить сообщение (для WebApp) ───────────────────────────────
@app.post("/api/create-prepared")
async def create_prepared(req: Request):
    payload = await req.json()
    user_id = int(payload["user_id"])
    caption = payload.get("text", "Готовая заготовка ✨")
    pim = await create_prepared_message(user_id, PHOTO_URL, caption)
    return {"id": pim["id"], "expiresAt": pim["expiration_date"]}

# ── RUN ────────────────────────────────────────────────────────────────────────
async def _main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import threading, uvicorn
    t = threading.Thread(target=lambda: uvicorn.run(app, host="0.0.0.0", port=8000), daemon=True)
    t.start()
    asyncio.run(_main())
