import os
import threading
import asyncio
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

SOURCE_CHATS = [-1002790633978]  # القروب المصدر
TARGET_CHAT = '@Twinssolo'       # القناة المستهدفة

active_accounts = {}
message_mapping = {}

def get_account_key(text):
    if not text:
        return None
    lines = text.strip().split('\n')
    return lines[0].strip() if lines else text

async def process_and_send(message):
    try:
        text = message.text or message.caption or ""
        if not text:
            return
        
        account_key = get_account_key(text)
        
        if account_key and account_key in active_accounts:
            old_target_msg_id = active_accounts[account_key]
            try:
                await client.delete_messages(TARGET_CHAT, old_target_msg_id)
            except Exception:
                pass
        
        supervisors_footer = "\n\nالمشرفين:\n@GZ232\n@i4Y0U"
        full_text = text + supervisors_footer

        if message.media:
            sent_msg = await client.send_file(TARGET_CHAT, message.media, caption=full_text)
        else:
            sent_msg = await client.send_message(TARGET_CHAT, full_text)
        
        if account_key:
            active_accounts[account_key] = sent_msg.id
        message_mapping[message.id] = sent_msg.id
    except Exception as e:
        print(f"Error processing message: {e}")

# مهمة دورية تعمل كل ساعة لفحص وسحب آخر 30 رسالة بأمان
async def hourly_sync_task():
    while True:
        try:
            print("Running hourly sync for the last 30 messages...")
            async for message in client.iter_messages(SOURCE_CHATS[0], limit=30):
                await process_and_send(message)
                # توقف قصير جداً بين كل رسالة والثانية لحماية الحساب من السبام
                await asyncio.sleep(1)
            print("Hourly sync completed successfully.")
        except Exception as e:
            print(f"Error in hourly sync: {e}")
        
        # الانتظار لمدة ساعة كاملة (3600 ثانية) قبل المرة القادمة
        await asyncio.sleep(3600)

@client.on(events.NewMessage(chats=SOURCE_CHATS))
async def new_message_handler(event):
    await process_and_send(event.message)
    print("New message processed and forwarded instantly!")

@client.on(events.MessageEdited(chats=SOURCE_CHATS))
async def edited_message_handler(event):
    try:
        if event.message.id in message_mapping:
            target_msg_id = message_mapping[event.message.id]
            new_text = event.message.text or event.message.caption or ""
            
            supervisors_footer = "\n\nالمشرفين:\n@GZ232\n@i4Y0U"
            updated_text = f"تم تخفيض الحد ⬇️\n\n{new_text}{supervisors_footer}"
            
            await client.edit_message(TARGET_CHAT, target_msg_id, updated_text)
            print("Message updated with new price and supervisors!")
    except Exception as e:
        print(f"Error in editing: {e}")

@client.on(events.MessageDeleted())
async def deleted_message_handler(event):
    try:
        for deleted_id in event.deleted_ids:
            if deleted_id in message_mapping:
                target_msg_id = message_mapping[deleted_id]
                await client.delete_messages(TARGET_CHAT, target_msg_id)
                del message_mapping[deleted_id]
                print("Message deleted from channel!")
    except Exception as e:
        print(f"Error in deleting: {e}")

async def main_bot_tasks():
    # تشغيل المهمة الدورية في الخلفية
    asyncio.create_task(hourly_sync_task())

    print("Telegram Bot is running and listening for real-time messages...")
    await client.run_until_disconnected()

def start_telegram_bot():
    client.start()
    client.loop.run_until_complete(main_bot_tasks())

if __name__ == '__main__':
    t = threading.Thread(target=start_telegram_bot)
    t.daemon = True
    t.start()
    run_flask()
    
