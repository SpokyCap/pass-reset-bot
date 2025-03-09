import os
import subprocess
import sys
import asyncio
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Enable logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

    url = "https://i.instagram.com/api/v1/accounts/send_password_reset/"  # IG password reset API
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "x-csrftoken": "vEG96oJnlEsyUWNS53bHLkVTMFYQKCBV"
    }
    
    data = {"user_email": user_input}
try:
    response = requests.post(url, headers=headers, data=data)
    
    formatted_response = f"```\n📩 Instagram Response:\n\nJSON\n{response.text}\n```"
    
    await update.message.reply_text(formatted_response, parse_mode="MarkdownV2")  # Enable markdown formatting
except Exception as e:
    logger.error(f"Error sending request: {e}")
    await update.message.reply_text("❌ An error occurred while processing your request.")


# 🔹 Start the Telegram bot
def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))  # Handle /start command
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_reset_request))  # Handle messages

    # Start the bot
    logger.info("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()  # Direct call instead of asyncio.run(main())
