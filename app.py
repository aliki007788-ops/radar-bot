from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = "8501855482:AAGCag1Dd2hdPpY4DMXu3-DQ9yATya6JT6c"

@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    print("پیام دریافتی:", data)
    return {"ok": True}

# مسیر تست برای مرورگر
@app.route("/status", methods=["GET"])
def status():
    return "Bot is running! ✅"
