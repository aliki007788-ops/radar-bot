Radar Deploy Bundle
===================

Contents:
- index.html          -> front-end with consent banner (integrated)
- app.py              -> Flask backend (simple, SQLite)
- requirements.txt
- Procfile            -> start command for Render / Heroku

Quick start (local):
1. Create virtualenv and install:
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

2. Run locally:
   export BOT_TOKEN="YOUR_BOT_TOKEN"
   export BOT_USERNAME="YourBotName"
   export ADMIN_WALLET="YOUR_WALLET_ADDRESS"
   export ADMIN_ID="123456789"
   python app.py

3. Open http://127.0.0.1:5000 in a browser (note: Telegram WebApp features require opening inside Telegram).

Deploy to Render (example):
1. Create a new Web Service on Render from Git repo or you can deploy by uploading code.
2. Use following start command (Render uses Docker/Gunicorn):
   gunicorn app:app

Set webhook (example using curl) -- replace placeholders:
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://<YOUR_RENDER_SERVICE>.onrender.com/<YOUR_BOT_TOKEN>"

If successful, Telegram returns {"ok":true,...}.

Security & Notes:
- This bundle uses SQLite for simplicity. For production, use PostgreSQL.
- Keep BOT_TOKEN and ADMIN_ID in environment variables, never commit to repo.
- Ensure HTTPS (Render provides it automatically).
- Consent banner is shown only to visitors (not to owners opening their own dashboard).

Files included in this zip:
- index.html
- app.py
- requirements.txt
- README.md
