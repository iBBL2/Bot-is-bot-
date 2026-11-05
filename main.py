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

SOURCE_CHATS = [-1002790633978]  # القروب المصدر
TARGET_CHAT = '@Twinssolo'       # القناة المستهدفة

# تخزين الحسابات النشطة لمعرفة التكرار وحذف القديم
active_accounts = {}
message_mapping = {}

def get_account_key(text):
    if not text:
        return None
    lines = text.strip().split('\n')
    return lines[0].strip() if lines else text

@client.on(events.NewMessage(chats=SOURCE_CHATS))
async def new_message_handler(event):
    try:
        text = event.message.text or event.message.caption or ""
        account_key = get_account_key(text)
        
        # إذا تكرر نشر نفس الحساب، احذف رسالته القديمة من القناة أولاً
        if account_key and account_key in active_accounts:
            old_target_msg_id = active_accounts[account_key]
            try:
                await client.delete_messages(TARGET_CHAT, old_target_msg_id)
                print("Old duplicate account message deleted from channel.")
            except Exception as e:
                print(f"Could not delete old message: {e}")
        
        # إضافة يوزرات المشرفين في نهاية الرسالة
        supervisors_footer = "\n\nالمشرفين:\n@GZ232\n@i4Y0U"
        full_text = text + supervisors_footer

        # إرسال الرسالة (مع الوسائط إن وجدت أو نص فقط)
        if event.message.media:
            sent_msg = await client.send_file(TARGET_CHAT, event.message.media, caption=full_text)
        else:
            sent_msg = await client.send_message(TARGET_CHAT, full_text)
        
        # تحديث السجلات
        if account_key:
            active_accounts[account_key] = sent_msg.id
        message_mapping[event.message.id] = sent_msg.id
        
        print("New message sent with supervisors successfully!")
    except Exception as e:
        print(f"Error in sending message: {e}")

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

def start_telegram_bot():
    print("Telegram Bot is running...")
    client.start()
    client.run_until_disconnected()

if __name__ == '__main__':
    t = threading.Thread(target=start_telegram_bot)
    t.daemon = True
    t.start()
    run_flask()
    
