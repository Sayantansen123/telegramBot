from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters,CommandHandler

# Replace with your own Telegram bot token from @BotFather
TELEGRAM_BOT_TOKEN = "8152120671:AAHPzUy-H6bQ7S3ZRVDQH3Hgn0RwiOphLBE"


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

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name
    message = update.message.text
    print(f"Message from {user}: {message}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Handle all text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CommandHandler("start", start))

    print("Bot is running... (Press CTRL+C to stop)")
    app.run_polling()