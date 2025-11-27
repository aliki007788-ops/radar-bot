import os
import sqlite3
import requests
import json
from flask import Flask, render_template, request, jsonify, abort
from datetime import datetime

app = Flask(__name__)

# ==========================================
# CONFIG & ADMIN SECRETS (از env بارگذاری شود)
# ==========================================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN")
BOT_USERNAME = os.environ.get("BOT_USERNAME", "YourBotName")
ADMIN_WALLET = os.environ.get("ADMIN_WALLET", "YOUR_WALLET_ADDRESS")
ADMIN_ID = os.environ.get("ADMIN_ID", "123456789")  # رشته یا عدد
TG_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ==========================================
# DATABASE HELPERS
# ==========================================
DB_PATH = os.environ.get("DB_PATH", "radar_global.db")

def get_db():
    # ساده‌ترین راه؛ برای اپ‌های پر بار از یک DB سرور استفاده کنید
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, first_name TEXT, joined_at TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS visits (id INTEGER PRIMARY KEY AUTOINCREMENT, owner_id INTEGER, visitor_id INTEGER, visitor_name TEXT, visitor_photo TEXT, timestamp TEXT, is_unlocked INTEGER DEFAULT 0, tx_hash TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)''')
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('price_usd', '0.5')")
    c.execute("INSERT OR IGNORE INTO settings (key, value) VALUES ('is_active', '1')")
    conn.commit()
    conn.close()

init_db()

def get_setting(key, default=None):
    conn = get_db()
    row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    conn.close()
    return row['value'] if row else default

def set_setting(key, value):
    conn = get_db()
    conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
    conn.commit()
    conn.close()

# ==========================================
# FINANCIAL ENGINE
# ==========================================
def get_ton_price():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=the-open-network&vs_currencies=usd"
        resp = requests.get(url, timeout=3)
        data = resp.json()
        return float(data['the-open-network']['usd'])
    except Exception:
        # fallback conservative
        return 7.0

def calculate_nanotons():
    price_usd = float(get_setting('price_usd', 0.5))
    ton_price = get_ton_price()
    ton_amount = price_usd / ton_price
    return int(ton_amount * 1_000_000_000), price_usd

# ==========================================
# TELEGRAM HELPERS
# ==========================================
def send_msg(chat_id, text, parse_mode=None):
    payload = {"chat_id": chat_id, "text": text}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    try:
        requests.post(f"{TG_API_URL}/sendMessage", json=payload, timeout=5)
    except Exception as e:
        app.logger.warning("Failed to send msg: %s", e)

# Simple admin check
def is_admin(chat_id):
    try:
        return str(chat_id) == str(ADMIN_ID)
    except Exception:
        return False

# ==========================================
# TELEGRAM WEBHOOK ENDPOINT (POST from Telegram)
# route uses token in path for simple auth (optional)
# ==========================================
@app.route(f"/{BOT_TOKEN}", methods=['POST'])
def telegram_webhook():
    update = request.get_json(force=True, silent=True)
    if not update:
        return "no payload", 400

    # handle messages
    if 'message' in update:
        msg = update['message']
        chat_id = msg['chat']['id']
        text = msg.get('text', '')

        if is_admin(chat_id):
            handle_admin_commands(chat_id, text)
        else:
            send_msg(chat_id, "Please use the App button to launch Radar.")
    return "OK", 200

def handle_admin_commands(chat_id, text):
    conn = get_db()
    c = conn.cursor()

    if text == '/stats':
        user_count = c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        visit_count = c.execute("SELECT COUNT(*) FROM visits").fetchone()[0]
        income_count = c.execute("SELECT COUNT(*) FROM visits WHERE is_unlocked=1").fetchone()[0]
        price = get_setting('price_usd', '0.5')
        msg = (f"📊 Empire Stats\n"
               f"👥 Users: {user_count}\n"
               f"👁️ Total Visits: {visit_count}\n"
               f"🔓 Unlocks (Sales): {income_count}\n"
               f"💵 Current Price: ${price}")
        send_msg(chat_id, msg)
    elif text and text.startswith('/setprice '):
        parts = text.split()
        if len(parts) >= 2:
            try:
                new_price = float(parts[1])
                set_setting('price_usd', new_price)
                send_msg(chat_id, f"✅ Price updated to ${new_price}")
            except ValueError:
                send_msg(chat_id, "❌ Invalid amount. Usage: /setprice 0.5")
        else:
            send_msg(chat_id, "❌ Usage: /setprice 0.5")
    elif text and text.startswith('/broadcast '):
        # broadcast is potentially heavy — انجام در پس‌زمینه بهتر است (اینجا ساده است)
        msg_text = text.replace('/broadcast ', '', 1)
        users = c.execute("SELECT id FROM users").fetchall()
        count = 0
        for u in users:
            try:
                send_msg(u['id'], msg_text)
                count += 1
            except Exception:
                continue
        send_msg(chat_id, f"📢 Sent to {count} users.")
    else:
        help_text = ("👮‍♂️ Admin Panel\n"
                     "/stats – View Statistics\n"
                     "/setprice [amount] – Change USD Price\n"
                     "/broadcast [msg] – Message All Users")
        send_msg(chat_id, help_text)

    conn.close()

# ==========================================
# APP ROUTES (Front-end + APIs)
# ==========================================
@app.route('/')
def index():
    return render_template('index.html', admin_wallet=ADMIN_WALLET, BOT_USERNAME=BOT_USERNAME)

@app.route('/api/get_price')
def api_get_price():
    nanotons, usd = calculate_nanotons()
    return jsonify({"usd": usd, "nanotons": nanotons})

@app.route('/api/track', methods=['POST'])
def track():
    data = request.get_json(force=True, silent=True) or {}
    owner_id = data.get('owner_id')
    visitor = data.get('visitor_data') or {}

    if not owner_id or not visitor:
        return jsonify({"error": "missing data"}), 400

    # جلوگیری از ثبت بازدید خودِ صاحب
    try:
        if str(owner_id) == str(visitor.get('id')):
            return jsonify({"status": "self"})

        conn = get_db()
        c = conn.cursor()

        # ثبت کاربر مالک (اگر موجود نباشد)
        c.execute("INSERT OR IGNORE INTO users (id, first_name, joined_at) VALUES (?, ?, ?)",
                  (owner_id, visitor.get('first_name', 'User'), datetime.utcnow().isoformat()))

        # ثبت بازدید
        c.execute("INSERT INTO visits (owner_id, visitor_id, visitor_name, visitor_photo, timestamp) VALUES (?, ?, ?, ?, ?)",
                  (owner_id, visitor.get('id'), visitor.get('first_name', ''), visitor.get('photo_url', ''), datetime.utcnow().isoformat()))
        conn.commit()
        conn.close()

        # (اختیاری) اطلاع به صاحب پروفایل در تلگرام
        # send_msg(owner_id, "🔔 New Visit Detected on Radar!")

        return jsonify({"status": "ok"})
    except Exception as e:
        app.logger.exception("track error")
        return jsonify({"error": "server error"}), 500

@app.route('/api/my_dashboard/<int:user_id>')
def dashboard(user_id):
    try:
        conn = get_db()
        rows = conn.execute("SELECT * FROM visits WHERE owner_id=? ORDER BY timestamp DESC", (user_id,)).fetchall()
        conn.close()
        result = [dict(r) for r in rows]
        return jsonify(result)
    except Exception:
        return jsonify([])

@app.route('/api/unlock', methods=['POST'])
def unlock():
    data = request.get_json(force=True, silent=True) or {}
    visit_id = data.get('visit_id')
    boc = data.get('boc')  # می‌توانید tx_hash واقعی را ذخیره کنید

    if not visit_id:
        return jsonify({"error": "missing visit id"}), 400

    try:
        conn = get_db()
        conn.execute("UPDATE visits SET is_unlocked=1, tx_hash=? WHERE id=?", (boc, visit_id))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception:
        app.logger.exception("unlock error")
        return jsonify({"success": False}), 500

if __name__ == '__main__':
    # برای محیط توسعه
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
