import os
import subprocess
import sys

# 🔹 Install required modules if missing
try:
    import requests
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
except ImportError:
    print("Installing required modules...")
    subprocess.run([sys.executable, "-m", "pip", "install", "requests", "python-telegram-bot"], check=True)
    import requests
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# 🔹 Replace this with your Telegram bot token from BotFather
TELEGRAM_BOT_TOKEN = "7544051823:AAGWFsIQqypz9-yPyCAC5v4cAzouqjsMqyA"

# 🔹 Function for /start command
async def start(update: Update, context: CallbackContext):
    welcome_msg = (
        "🤖 Welcome to the Insta Reset Bot!\n\n"
        "🔹 Send me your Instagram username/email, and I'll request a password reset for you.\n"
        "           ~By @spokycap | @Cyberjurks\n\n "
    )
    await update.message.reply_text(welcome_msg)

# 🔹 Function to handle incoming messages
async def send_reset_request(update: Update, context: CallbackContext):
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
    await update.message.reply_text(f"📩 Instagram Response:\n{response.text}")

# 🔹 Start the Telegram bot
def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))  # Handle /start command
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_reset_request))  # Handle messages

    # Start the bot
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
