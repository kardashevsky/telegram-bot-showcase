from dotenv import load_dotenv
from html import escape
from datetime import datetime, timezone
import os, asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from prepared import create_prepared_message

INVITE_TEXT = (
    "Привет! Это инвайт в GENZA — первый геймифицированный дейтинг в Telegram.\n\n"
    "Здесь AI соединяет людей по вайбу и ценностям, а не только по фото.\n\n"
    "Переходи по моей ссылке — получишь 1000 монет, а я — бонус 🚀"
)

load_dotenv()
BOT_TOKEN = os.environ["BOT_TOKEN"]
WEBAPP_URL = os.environ["WEBAPP_URL"]
PHOTO_URL  = os.environ["PHOTO_URL"]

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def on_start(m):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Open Mini App", url=WEBAPP_URL)]]
    )
    # отправляем инвайт с фото
    await m.answer_photo(photo=PHOTO_URL, caption=INVITE_TEXT, reply_markup=kb, parse_mode="HTML")

    # готовим заготовку и шлём id в HTML
    pim = await create_prepared_message(
        bot_token=BOT_TOKEN,
        user_id=m.from_user.id,
        photo_url=PHOTO_URL,
        caption=INVITE_TEXT,
        webapp_url=WEBAPP_URL,
    )
    exp_iso = datetime.fromtimestamp(pim["expiration_date"], tz=timezone.utc).isoformat()
    await m.answer(
        f"message_id: <code>{escape(pim['id'])}</code>\nexpires: <code>{exp_iso}</code>",
        parse_mode="HTML",
    )

async def _main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(_main())
