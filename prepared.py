import time, httpx

async def create_prepared_message(*, bot_token: str, user_id: int, photo_url: str,
                                  caption: str, webapp_url: str) -> dict:
    api_url = f"https://api.telegram.org/bot{bot_token}/savePreparedInlineMessage"

    result = {
        "type": "photo",
        "id": str(int(time.time() * 1000)),
        "photo_url": photo_url,
        "thumb_url": photo_url,
        "title": "GENZA",
        "caption": caption,
        "reply_markup": {
            "inline_keyboard": [[{"text": "Open Mini App", "url": webapp_url}]]
        },
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
        r = await client.post(api_url, json=payload)
        r.raise_for_status()
        return r.json()["result"]  # {"id": "...", "expiration_date": ...}
