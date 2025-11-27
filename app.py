from flask import Flask, request, abort

app = Flask(__name__)

BOT_TOKEN = "8501855482:AAGCag1Dd2hdPpY4DMXu3-DQ9yATya6JT6c"

@app.route('/')
def index():
    return "Bot is running!"

@app.route(f'/webhook/{BOT_TOKEN}', methods=['POST'])
def webhook():
    if request.method == 'POST':
        update = request.get_json()
        print(update)  # اینجا پیام‌های دریافتی تلگرام چاپ می‌شود
        return {"ok": True}
    else:
        abort(405)  # Method Not Allowed برای غیر POST

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
