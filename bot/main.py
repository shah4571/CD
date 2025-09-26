# bot/main.py

import asyncio
import os
import time
import nest_asyncio
from pyrogram import Client
from bot.config import BOT_TOKEN, API_ID, API_HASH
from bot.handlers import init_handlers

# Fix asyncio loop reuse issues
nest_asyncio.apply()

# -----------------------------
# ✅ Force VPS system time sync (ntpdate enough)
os.system("sudo ntpdate -u pool.ntp.org")
time.sleep(3)  # ৩ সেকেন্ড অপেক্ষা

# Optional: পুরনো session ব্যাকআপ/মুছে ফেলা
SESSION_FILE = "RajuNewBot.session"
if os.path.exists(SESSION_FILE):
    os.rename(SESSION_FILE, SESSION_FILE + ".bak")

# -----------------------------
# ✅ Pyrogram time override helper
import pyrogram
import datetime

class TimeFixedClient(Client):
    async def send(self, *args, **kwargs):
        # Pyrogram session start করার আগে local clock adjust
        now = datetime.datetime.utcnow()
        self._start_time = int(now.timestamp())  # override start time
        return await super().send(*args, **kwargs)

# -----------------------------
async def main():
    # ✅ Create Pyrogram Client
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

    # Register handlers
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
