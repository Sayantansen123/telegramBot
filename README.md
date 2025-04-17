# 🤖 Telegram to Discord Bridge Bot

A simple Python Telegram bot that allows each user to initialize their own Discord Webhook and send messages from Telegram to their Discord server using commands.

---

## 🚀 Features

- ✅ User-specific Discord webhook storage
- ✅ MongoDB integration for persistent webhook mapping
- ✅ Telegram commands: `/start`, `/initialize`, `/send`
- ✅ Sends Telegram messages directly to Discord
- ✅ Secrets stored securely in `.env`

---

## 📦 Tech Stack

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [pymongo](https://pymongo.readthedocs.io/)
- [requests](https://docs.python-requests.org/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)

---

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/telegram-discord-bot.git
cd telegram-discord-bot

2.Create Virtual Environment (Optional but recommended)

python -m venv venv
source venv/bin/activate

3.Install dependecies
pip install -r requirements.txt