# bot/main.py
import asyncio
import os
import datetime
from pyrogram import Client
from bot.config import BOT_TOKEN, API_ID, API_HASH
from bot.handlers import init_handlers

# -----------------------------
# ✅ Fresh session helper
SESSION_FILE = "RajuNewBot.session"
if os.path.exists(SESSION_FILE):
    # পুরনো session backup
    os.rename(SESSION_FILE, SESSION_FILE + ".bak")

# -----------------------------
# Optional: Time override (microsecond safe)
class TimeSafeClient(Client):
    async def start(self):
        # Pyrogram start time fix for VPS
        now = datetime.datetime.utcnow()
        self._start_time = int(now.timestamp())
        return await super().start()

# -----------------------------
async def main():
    # Create client
    app = TimeSafeClient(
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

    # Register handlers
    init_handlers(app)

    print("[INFO] Bot is starting...")

    async with app:
        print("[INFO] Bot is running!")
        await app.idle()

# -----------------------------
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("[INFO] Bot stopped manually")
