from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters,CommandHandler
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Replace with your own Telegram bot token from @BotFather
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# In-memory user webhook store: {user_id: discord_webhook_url}
user_webhooks = {}

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
        webhook_url = context.args[0]
        if webhook_url.startswith("https://discord.com/api/webhooks/"):
            user_webhooks[user_id] = webhook_url
            await update.message.reply_text("✅ Discord webhook initialized successfully.")
        else:
            await update.message.reply_text("⚠️ Invalid Discord webhook URL.")
    else:
        await update.message.reply_text("Usage: /initialize <discord_webhook_url>")

async def send_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name

    if user_id not in user_webhooks:
        await update.message.reply_text("⚠️ Please initialize your Discord webhook first using /initialize <webhook_url>.")
        return

    if not context.args:
        await update.message.reply_text("⚠️ Please provide a message to send.")
        return

    message = ' '.join(context.args)
    discord_message = f"**{user_name} says:** {message}"
    webhook_url = user_webhooks[user_id]

    # Send to Discord
    response = requests.post(webhook_url, json={"content": discord_message})
    if response.status_code == 204:
        await update.message.reply_text("✅ Message sent to Discord!")
    else:
        await update.message.reply_text("❌ Failed to send message to Discord.")

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