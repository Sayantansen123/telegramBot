from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters,CommandHandler
import requests
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

load_dotenv()

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

💬 Just type:
`/send Hello Discord!`

🔒 Only authorized users can use this bot (if enabled).
⚙️ More features coming soon!

Type /help to see available commands.

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

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Handle all text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("send", send_command))
    app.add_handler(CommandHandler("initialize", initialize))


    print("Bot is running... (Press CTRL+C to stop)")
    app.run_polling()