# bot/main.py

import asyncio
import os
import time
import nest_asyncio
import datetime
from pyrogram import Client
from bot.config import BOT_TOKEN, API_ID, API_HASH
from bot.handlers import init_handlers

# Fix asyncio loop reuse issues
nest_asyncio.apply()

# -----------------------------
# ✅ Optional: পুরনো session ব্যাকআপ
SESSION_FILE = "RajuNewBot.session"
if os.path.exists(SESSION_FILE):
    os.rename(SESSION_FILE, SESSION_FILE + ".bak")

# -----------------------------
# ✅ Time override helper for Pyrogram
class TimeFixedClient(Client):
    async def start(self):
        # start করার আগে local clock fix
        now = datetime.datetime.utcnow()
        self._start_time = int(now.timestamp())
        return await super().start()

# -----------------------------
async def main():
    # ✅ Create Pyrogram client
    app = TimeFixedClient(
        "RajuNewBot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        parse_mode="html",
        ipv6=False,
        device_model="VPS",
        app_version="1.0",
        lang_code="en"
    )

    # Register all handlers
    init_handlers(app)

    print("[INFO] Bot is starting...")

    async with app:
        print("[INFO] Bot is running!")
        await app.idle()

# -----------------------------
if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except (KeyboardInterrupt, SystemExit):
        print("[INFO] Bot stopped manually")
