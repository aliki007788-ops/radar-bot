1. Set environment variables: BOT_TOKEN, BOT_USERNAME, ADMIN_WALLET, ADMIN_ID
2. Deploy on Render (Web Service)
3. Start command: gunicorn app:app
4. Set Telegram Webhook:
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://<YOUR_RENDER_SERVICE>.onrender.com/webhook/<YOUR_BOT_TOKEN>"
5. Open bot inside Telegram, click App, enjoy full Radar features.
