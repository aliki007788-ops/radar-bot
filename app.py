from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = "8501855482:AAGCag1Dd2hdPpY4DMXu3-DQ9yATya6JT6c"

# مسیر وب‌هوک باید دقیقاً با توکن همخوانی داشته باشد
@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    print("پیام دریافتی:", data)  # برای تست و دیباگ
    return {"ok": True}

# مسیر تست ساده برای اطمینان از اینکه سرویس بالا است
@app.route("/")
def index():
    return "Bot is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
