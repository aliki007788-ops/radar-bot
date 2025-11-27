from flask import Flask, request

app = Flask(__name__)

# === جایگزین کن با توکن ربات خودت ===
BOT_TOKEN = "8501855482:AAGCag1Dd2hdPpY4DMXu3-DQ9yATya6JT6c"

# مسیر وب‌هوک امن
@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    print("دیتای دریافتی از تلگرام:", data)
    return {"ok": True}

# مسیر تست ساده
@app.route("/")
def index():
    return "Bot is running!"

if __name__ == "__main__":
    # Render خودش پورت را تنظیم می‌کند، پس از PORT محیطی استفاده می‌کنیم
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
