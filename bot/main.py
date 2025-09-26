# bot/main.py

import asyncio
import os
import time
import nest_asyncio
from pyrogram import Client
from bot.config import BOT_TOKEN, API_ID, API_HASH
from bot.handlers import init_handlers

# -----------------------------
# ✅ Fix asyncio loop reuse issues
nest_asyncio.apply()

# -----------------------------
# ✅ VPS / Python time resync
# NTP service ensure and force sync before starting Pyrogram
os.system("sudo timedatectl set-ntp true")
os.system("sudo systemctl restart systemd-timesyncd")
os.system("sudo ntpdate -u pool.ntp.org")
time.sleep(2)  # ২ সেকেন্ড অপেক্ষা, Python session আগে টাইম ঠিক হয়

# -----------------------------
# Optional: পুরনো session ব্যাকআপ/মুছে ফেলা
SESSION_FILE = "RajuNewBot.session"
if os.path.exists(SESSION_FILE):
    os.rename(SESSION_FILE, SESSION_FILE + ".bak")  # backup হিসেবে রাখবে

# -----------------------------
async def main():
    # ✅ Create Pyrogram Client
    app = Client(
        "RajuNewBot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        parse_mode="html",
        ipv6=False,
        # Device info (VPS-friendly)
        system_version=None,
        system_lang_code="en",
        device_model="VPS",
        app_version="1.0",
        lang_code="en"
    )

    # Register all bot handlers
    init_handlers(app)

    print("[INFO] Bot is starting...")

    # Start bot
    async with app:
        print("[INFO] Bot is running!")
        await app.idle()

# -----------------------------
if __name__ == "__main__":
    try:
        # Python 3.11/3.12 compatible event loop
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except (KeyboardInterrupt, SystemExit):
        print("[INFO] Bot stopped manually")
