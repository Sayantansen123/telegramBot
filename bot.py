from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters,CommandHandler
import requests
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from telegram.constants import ChatAction

load_dotenv()

DISCORD_MAX_FILE_SIZE = 2.5 * 1024 * 1024  # 2.5 MB in bytes
send_file_ready = {}

# Replace with your own Telegram bot token from @BotFather
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
# In-memory user webhook store: {user_id: discord_webhook_url}

# Connect to MongoDB
try:
    client = MongoClient(MONGO_URI)
    client.admin.command('ping')  # Check connection
    print("✅ Connected to MongoDB")
except ConnectionFailure as e:
    print("❌ MongoDB connection failed:", e)
    exit(1)
db = client["telegram_bot"]
collection = db["webhooks"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name
    welcome_message = f"""
👋 Hello {user}!

I'm divineBot, your bridge between Telegram and Discord.  
Here’s what I can do for you:

📤 Use the command `/send <your message>` to send a message to a connected Discord server.
📤 Use the command `/initialize <webhook_url>` to send a message to a connect a Discord server.
📤 Use the command `/sendFile ` then send the file to send a file and image to a Discord server.
📤 Use the command `/discordHook ` to know how to get the discordHook of the discord server.

💬 Just type:
`/send Hello Discord!`

⚙️ More features coming soon!

Type /start to see available commands.

🚀 Let's get started!
    """
    await update.message.reply_markdown(welcome_message)

# /initialize <webhook_url>
async def initialize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if context.args:
        webhook = context.args[0]
        if webhook.startswith("https://discord.com/api/webhooks/"):
            # Upsert user webhook
            collection.update_one(
                {"user_id": user_id},
                {"$set": {"webhook": webhook}},
                upsert=True
            )
            await update.message.reply_text("✅ Webhook saved to database.")
        else:
            await update.message.reply_text("⚠️ Invalid Discord webhook URL.")
    else:
        await update.message.reply_text("Usage: /initialize <discord_webhook_url>")

async def send_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name

    user_data = collection.find_one({"user_id": user_id})
    if not user_data:
        await update.message.reply_text("⚠️ Please initialize your Discord webhook first. /initialize <webhook_url>.")
        return

    if not context.args:
        await update.message.reply_text("⚠️ Please provide a message to send.")
        return

    message = ' '.join(context.args)
    webhook_url = user_data['webhook']
    discord_message = f"From telegram **{user_name} says:** {message}"

    response = requests.post(webhook_url, json={"content": discord_message})
    if response.status_code == 204:
        await update.message.reply_text("✅ Message sent to Discord!")
    else:
        await update.message.reply_text("❌ Failed to send to Discord.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name
    message = update.message.text
    print(f"Message from {user}: {message}")

async def send_file_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = collection.find_one({"user_id": user_id})
    if not user or "webhook" not in user:
        await update.message.reply_text("❌ Please initialize your Discord webhook first using /initialize.")
        return

    send_file_ready[user_id] = True
    await update.message.reply_text("📎 Please now send the image or document (max 2.5MB) you want to send.")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    userName = update.effective_user.first_name
    user_id = update.effective_user.id
    if not send_file_ready.get(user_id):
        return  # Ignore if not triggered via /sendFile

    send_file_ready[user_id] = False
    document = update.message.document
    file = await document.get_file()
    file_path = f"{user_id}_{document.file_name}"
    await file.download_to_drive(file_path)

    file_size = os.path.getsize(file_path)
    if file_size > 2.5 * 1024 * 1024:
        os.remove(file_path)
        await update.message.reply_text("❌ File too large! Max file size is 2.5MB.")
        return

    user = collection.find_one({"user_id": user_id})
    webhook_url = user["webhook"]

    with open(file_path, 'rb') as doc:
        requests.post(webhook_url, files={"file": doc}, data={"content": f"📎 File from Telegram user {userName}"})

    os.remove(file_path)
    await update.message.reply_text("✅ File sent successfully to Discord!")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    userName = update.effective_user.first_name
    user_id = update.effective_user.id
    if not send_file_ready.get(user_id):
        return

    send_file_ready[user_id] = False
    photo = update.message.photo[-1]
    file = await photo.get_file()
    file_path = f"{user_id}_photo.jpg"
    await file.download_to_drive(file_path)

    file_size = os.path.getsize(file_path)
    if file_size > 2.5 * 1024 * 1024:
        os.remove(file_path)
        await update.message.reply_text("❌ File too large! Max file size is 2.5MB.")
        return

    user = collection.find_one({"user_id": user_id})
    webhook_url = user["webhook"]

    with open(file_path, 'rb') as img:
        requests.post(webhook_url, files={"file": img}, data={"content": f"📷 Image from Telegram user {userName}"})

    os.remove(file_path)
    await update.message.reply_text("✅ Image sent successfully to Discord!")

async def discord_hook_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Show typing/loading while uploading
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_VIDEO)

    await update.message.reply_text(
        "🎬 Here's a video guide to help you get your Discord webhook URL:"
    )

    with open("videoplayback.mp4", "rb") as video_file:
        await update.message.reply_video(
            video=video_file,
            caption=(
                "🔗 Steps:\n"
                "1. Open your Discord Server\n"
                "2. Go to a channel → ⚙️ Edit Channel → Integrations\n"
                "3. Create/Copy Webhook\n"
                "4. Use `/initialize <webhook_url>` here\n\n"
                "You're all set! 🚀"
            )
        )


if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Handle all text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("send", send_command))
    app.add_handler(CommandHandler("initialize", initialize))
    app.add_handler(CommandHandler("sendFile", send_file_command))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(CommandHandler("discordHook", discord_hook_guide))


    print("Bot is running... (Press CTRL+C to stop)")
    app.run_polling()