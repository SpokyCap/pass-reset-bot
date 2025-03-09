import os
import subprocess
import sys

# 🔹 Install required modules if missing
try:
    import requests
    from telegram import Update
    from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
except ImportError:
    print("Installing required modules...")
    subprocess.run([sys.executable, "-m", "pip", "install", "requests", "python-telegram-bot"], check=True)
    import requests
    from telegram import Update
    from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# 🔹 Replace this with your Telegram bot token from BotFather
TELEGRAM_BOT_TOKEN = "7544051823:AAGWFsIQqypz9-yPyCAC5v4cAzouqjsMqyA"

# 🔹 Function for /start command
def start(update: Update, context: CallbackContext):
    welcome_msg = (
        "🤖 Welcome to the Insta Reset Bot!\n\n"
        "🔹 Send me your Instagram username/email, and I'll request a password reset for you.\n"
        "           ~By @spokycap | @Cyberjurks\n\n "
    )
    update.message.reply_text(welcome_msg, parse_mode="Markdown")

# 🔹 Function to handle incoming messages
def send_reset_request(update: Update, context: CallbackContext):
    user_input = update.message.text.strip()  # Get user input (username/email)

    # Instagram password reset API
    url = "https://i.instagram.com/api/v1/accounts/send_password_reset/"
    
    # Headers (exactly as you wanted)
    headers = {
        "User-Agent": "Mozilla/5.0",
        "x-csrftoken": "vEG96oJnlEsyUWNS53bHLkVTMFYQKCBV"
    }
    
    # Data payload
    data = {
        "user_email": user_input
    }
    
    # Send request
    response = requests.post(url, headers=headers, data=data)

    # Send the response back to Telegram
    update.message.reply_text(f"📩 Instagram Response:\n{response.text}", parse_mode="Markdown")

# 🔹 Start the Telegram bot
def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Command handlers
    dp.add_handler(CommandHandler("start", start))  # Handle /start command
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, send_reset_request))  # Handle messages

    # Start the bot
    updater.start_polling()
    updater.idle()

if _name_ == "_main_":
    main()
