# bot/main.py

import asyncio
import os
import nest_asyncio
from pyrogram import Client
from bot.config import BOT_TOKEN, API_ID, API_HASH
from bot.handlers import init_handlers
import time

# Fix asyncio loop reuse issues
nest_asyncio.apply()

# Optional: পুরনো session ব্যাকআপ
SESSION_FILE = "RajuNewBot.session"
if os.path.exists(SESSION_FILE):
    os.rename(SESSION_FILE, SESSION_FILE + ".bak")

# -----------------------------
async def main():
    # Minimal Pyrogram client
    app = Client(
        "RajuNewBot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        parse_mode="html",
        ipv6=False
    )

    # Register handlers
    init_handlers(app)

    print("[INFO] Bot is starting...")

    # Start bot
    async with app:
        print("[INFO] Bot is running!")
        await app.idle()

# -----------------------------
if __name__ == "__main__":
    try:
        # Important: ensure Python sees correct UTC timestamp
        import time
        # small sleep to stabilize system clock
        time.sleep(1)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except (KeyboardInterrupt, SystemExit):
        print("[INFO] Bot stopped manually")
