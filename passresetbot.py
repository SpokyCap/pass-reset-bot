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

# Function for /start command
async def start(update: Update, context: CallbackContext):
    welcome_msg = (
        "💀 *Welcome to Insta Reset Bot!* 💀\n\n"
        "🚀 *Need a password reset?* I got you! Just send me your Instagram username or email, and I'll request a reset for you.\n\n"
        "🔹 *Fast, Secure & Hassle-Free!*\n"
        "🔹 *Stay in control of your account.*\n\n"
        "📌 *Created by:* @spokycap | @Cyberjurks"
    )
    await update.message.reply_text(welcome_msg, parse_mode="MarkdownV2")


import json

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
        
        # Load JSON response for pretty formatting
        response_json = json.loads(response.text)
        formatted_json = json.dumps(response_json, indent=2)  # Pretty print JSON
        
        # Escape special characters for MarkdownV2
        formatted_json = formatted_json.replace(".", "\\.").replace("-", "\\-").replace("_", "\\_")
        
        formatted_response = f"📩 Instagram Response:\n```\n{formatted_json}\n```"
        
        await update.message.reply_text(formatted_response, parse_mode="MarkdownV2")

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
