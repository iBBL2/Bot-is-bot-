from telethon import TelegramClient, events

api_id = 36835218
api_hash = '61b5955b5646397e808a5336e3c59359'

client = TelegramClient('bot_session', api_id, api_hash)

@client.on(events.NewMessage)
async def handler(event):
    # ضع هنا كود إعادة التوجيه الخاص بك
    pass

print("Bot is running...")
client.start()
client.run_until_disconnected()
