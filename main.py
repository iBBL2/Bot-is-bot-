import os
import threading
from flask import Flask
from telethon import TelegramClient, events

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

api_id = 36835218
api_hash = '61b5955b5646397e808a5336e3c59359'

client = TelegramClient('bot_session', api_id, api_hash)

@client.on(events.NewMessage)
async def handler(event):
    # ضع هنا كود إعادة التوجيه الخاص بك
    pass

def start_telegram_bot():
    print("Telegram Bot is running...")
    client.start()
    client.run_until_disconnected()

if __name__ == '__main__':
    t = threading.Thread(target=start_telegram_bot)
    t.daemon = True
    t.start()
    run_flask()
