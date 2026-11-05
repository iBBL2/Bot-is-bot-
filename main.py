import os
import threading
import asyncio
from flask import Flask
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# إعداد سيرفر الويب ليتوافق مع متطلبات منصة Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Telegram UserBot is active and running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# إعدادات التيليجرام وبيانات الاعتماد
api_id = int(os.environ.get("API_ID", 36835218))
api_hash = os.environ.get("API_HASH", "61b5955b5646397e808a5336e3c59359")
session_string = os.environ.get("SESSION_STRING")

SOURCE_CHAT_ID = -1002790633978
TARGET_CHAT = "@Twinssolo"
SUPERVISORS = "@GZ232 @i4Y0U"

client = TelegramClient(StringSession(session_string), api_id, api_hash)

# سجل لمنع تكرار معالجة الرسائل (Deduplication)
processed_messages = set()

async def process_and_forward(message):
    if not message.text:
        return
    
    # التحقق من عدم معالجة الرسالة مسبقاً
    if message.id in processed_messages:
        return
    processed_messages.add(message.id)
    
    text = message.text
    
    # إضافة التوقيعات إذا لم تكن موجودة مسبقاً في النص
    if "@GZ232" not in text and "@i4Y0U" not in text:
        text = f"{text}\n\n{SUPERVISORS}"
        
    try:
        await client.send_message(TARGET_CHAT, text)
    except Exception as e:
        print(f"Error forwarding message: {e}")

# استقبال وتوجيه الرسائل الجديدة في الوقت الفعلي
@client.on(events.NewMessage(chats=SOURCE_CHAT_ID))
async def handler(event):
    await process_and_forward(event.message)

async def sync_recent_messages():
    try:
        # جلب ومعالجة آخر 30 رسالة عند بدء التشغيل لضمان مزامنة الحالة
        async for message in client.iter_messages(SOURCE_CHAT_ID, limit=30):
            await process_and_forward(message)
    except Exception as e:
        print(f"Error in sync task: {e}")

async def main_bot():
    await client.start()
    print("UserBot started and connected successfully!")
    
    # تنفيذ مزامنة آخر 30 رسالة
    await sync_recent_messages()
    
    await client.run_until_disconnected()

if __name__ == '__main__':
    # تشغيل سيرفر الويب في خلفية النظام
    web_thread = threading.Thread(target=run_web)
    web_thread.start()
    
    # تشغيل حلقة أحداث بوت التليجرام
    asyncio.run(main_bot())
