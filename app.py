from flask import Flask, request
import os

app = Flask(__name__)

# توکن ربات خودت رو از محیط (Environment Variable) بخون
BOT_TOKEN = os.getenv("BOT_TOKEN")

@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.json
    print("Received update:", data)  # برای دیباگ
    return "ok", 200

@app.route("/")
def index():
    return "Bot is running!"
