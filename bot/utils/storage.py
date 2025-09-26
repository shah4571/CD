import json
import os
from datetime import datetime

# ---------------- Base Directories ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, "users.json")
COUNTRY_FILE = os.path.join(BASE_DIR, "country_rates.json")
SESSION_FILE = os.path.join(BASE_DIR, "session_settings.json")
WITHDRAW_FILE = os.path.join(BASE_DIR, "withdraw_requests.json")
OPEN_COUNTRY_FILE = os.path.join(BASE_DIR, "open_countries.json")
ADMIN_LOGS_FILE = os.path.join(BASE_DIR, "admin_logs.json")
FAILED_VERIF_FILE = os.path.join(BASE_DIR, "failed_verifications.json")
TEMPLATE_FILE = os.path.join(BASE_DIR, "template_messages.json")
TRANSACTION_LOG_FILE = os.path.join(BASE_DIR, "transaction_logs.json")
SESSION_COUNTER_FILE = os.path.join(BASE_DIR, "session_counter.json")
MAINT_MODE_FILE = os.path.join(BASE_DIR, "maintenance_mode.json")
TWO_FA_FILE = os.path.join(BASE_DIR, "2fa_password.json")

# ------------------ Users ------------------ #
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def get_user_info(uid):
    users = load_users()
    return users.get(str(uid))

def update_user_info(uid, data):
    users = load_users()
    u = users.get(str(uid), {})
    u.update(data)
    users[str(uid)] = u
    save_users(users)

def get_all_users():
    users = load_users()
    return [{"id": int(uid), **info} for uid, info in users.items()]

def ban_user(uid):
    update_user_info(uid, {"banned": True})

def unban_user(uid):
    update_user_info(uid, {"banned": False})

def delete_user(uid):
    users = load_users()
    users.pop(str(uid), None)
    save_users(users)

def force_logout_users():
    users = load_users()
    for uid, info in users.items():
        info["logged_in"] = False
    save_users(users)

def get_user_stats(uid):
    user = get_user_info(uid)
    if not user:
        return {}
    return {
        "id": uid,
        "balance": user.get("balance", 0),
        "sessions": user.get("sessions", 0),
        "banned": user.get("banned", False),
        "joined": user.get("joined", str(datetime.utcnow()))
    }

# ------------------ Country Rates ------------------ #
def load_country_rates():
    if not os.path.exists(COUNTRY_FILE):
        return {}
    with open(COUNTRY_FILE, "r") as f:
        return json.load(f)

def save_country_rates(rates):
    with open(COUNTRY_FILE, "w") as f:
        json.dump(rates, f, indent=4)

def get_country_rates():
    return load_country_rates()

def set_country_rate(country, price, time=3600, status="ON"):
    rates = load_country_rates()
    rates[country.upper()] = {"price": float(price), "time": int(time), "status": status.upper()}
    save_country_rates(rates)

def close_country(country):
    rates = load_country_rates()
    c = country.upper()
    if c in rates:
        rates[c]["status"] = "OFF"
        save_country_rates(rates)

def toggle_country_status(country):
    rates = load_country_rates()
    c = country.upper()
    if c in rates:
        rates[c]["status"] = "ON" if rates[c]["status"] == "OFF" else "OFF"
        save_country_rates(rates)

# ------------------ Session Settings ------------------ #
def load_session_settings():
    if not os.path.exists(SESSION_FILE):
        return {"timeout": 7200}
    with open(SESSION_FILE, "r") as f:
        return json.load(f)

def save_session_settings(settings):
    with open(SESSION_FILE, "w") as f:
        json.dump(settings, f, indent=4)

def set_session_timeout(seconds):
    settings = load_session_settings()
    settings["timeout"] = int(seconds)
    save_session_settings(settings)

def get_session_timeout():
    settings = load_session_settings()
    return settings.get("timeout", 7200)

# ------------------ Withdraw Requests ------------------ #
def load_withdraw_requests():
    if not os.path.exists(WITHDRAW_FILE):
        return []
    with open(WITHDRAW_FILE, "r") as f:
        return json.load(f)

def save_withdraw_requests(requests):
    with open(WITHDRAW_FILE, "w") as f:
        json.dump(requests, f, indent=4)

def mark_withdraw_request(uid, method, amount, wallet_address):
    requests = load_withdraw_requests()
    requests.append({
        "user_id": uid,
        "method": method,
        "amount": amount,
        "wallet_address": wallet_address,
        "timestamp": datetime.utcnow().isoformat()
    })
    save_withdraw_requests(requests)

# ------------------ Open Countries ------------------ #
def load_open_countries():
    if not os.path.exists(OPEN_COUNTRY_FILE):
        return []
    with open(OPEN_COUNTRY_FILE, "r") as f:
        return json.load(f)

def save_open_countries(countries):
    with open(OPEN_COUNTRY_FILE, "w") as f:
        json.dump(countries, f, indent=4)

def add_open_country(country):
    countries = load_open_countries()
    c = country.upper()
    if c not in countries:
        countries.append(c)
    save_open_countries(countries)

def get_open_countries():
    return load_open_countries()

# ------------------ Admin Logs ------------------ #
def view_admin_logs():
    if not os.path.exists(ADMIN_LOGS_FILE):
        return []
    with open(ADMIN_LOGS_FILE, "r") as f:
        return json.load(f)

def log_admin_action(action, uid):
    logs = view_admin_logs()
    logs.append({"action": action, "user_id": uid, "timestamp": datetime.utcnow().isoformat()})
    with open(ADMIN_LOGS_FILE, "w") as f:
        json.dump(logs, f, indent=4)

# ------------------ Failed Verifications ------------------ #
def get_failed_verifications():
    if not os.path.exists(FAILED_VERIF_FILE):
        return []
    with open(FAILED_VERIF_FILE, "r") as f:
        return json.load(f)

def add_failed_verification(uid):
    data = get_failed_verifications()
    data.append({"user_id": uid, "time": datetime.utcnow().isoformat()})
    with open(FAILED_VERIF_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ------------------ Transaction Logs ------------------ #
def get_transaction_logs():
    if not os.path.exists(TRANSACTION_LOG_FILE):
        return []
    with open(TRANSACTION_LOG_FILE, "r") as f:
        return json.load(f)

def add_transaction(uid, method, amount):
    logs = get_transaction_logs()
    logs.append({"user_id": uid, "method": method, "amount": amount, "timestamp": datetime.utcnow().isoformat()})
    with open(TRANSACTION_LOG_FILE, "w") as f:
        json.dump(logs, f, indent=4)

# ------------------ Template Messages ------------------ #
def template_messages():
    if not os.path.exists(TEMPLATE_FILE):
        with open(TEMPLATE_FILE, "w") as f:
            json.dump([], f)
    with open(TEMPLATE_FILE, "r") as f:
        messages = json.load(f)
    return messages  # Returns list of templates

def add_template_message(message):
    messages = template_messages()
    messages.append(message)
    with open(TEMPLATE_FILE, "w") as f:
        json.dump(messages, f, indent=4)

# ------------------ Maintenance Mode ------------------ #
def maintenance_mode(enable=True):
    with open(MAINT_MODE_FILE, "w") as f:
        json.dump({"enabled": enable}, f)

def is_maintenance_mode():
    if not os.path.exists(MAINT_MODE_FILE):
        return False
    with open(MAINT_MODE_FILE, "r") as f:
        data = json.load(f)
    return data.get("enabled", False)

# ------------------ Session Counter ------------------ #
def reset_session_counter():
    with open(SESSION_COUNTER_FILE, "w") as f:
        json.dump({"counter": 0}, f)

def auto_session_stats():
    if not os.path.exists(SESSION_COUNTER_FILE):
        return {"counter": 0}
    with open(SESSION_COUNTER_FILE, "r") as f:
        return json.load(f)

# ------------------ Scheduled / Targeted Broadcast ------------------ #
def scheduled_broadcast(message):
    users = get_all_users()
    sent, failed = 0, 0
    for u in users:
        try:
            # এখানে placeholder: Bot send_message logic
            sent += 1
        except:
            failed += 1
    return {"sent": sent, "failed": failed}

def targeted_broadcast(message, target_ids):
    sent, failed = 0, 0
    for uid in target_ids:
        try:
            # placeholder: Bot send_message logic
            sent += 1
        except:
            failed += 1
    return {"sent": sent, "failed": failed}

# ------------------ 2FA ------------------ #
def change_2fa_password(new_pass):
    with open(TWO_FA_FILE, "w") as f:
        json.dump({"2fa": new_pass}, f)

def get_2fa_password():
    if not os.path.exists(TWO_FA_FILE):
        return None
    with open(TWO_FA_FILE, "r") as f:
        data = json.load(f)
    return data.get("2fa")
