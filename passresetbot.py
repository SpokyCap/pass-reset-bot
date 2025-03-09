import json
import logging
import requests
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# Enable logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🔹 Replace this with your Telegram bot token
TELEGRAM_BOT_TOKEN = "7544051823:AAGWFsIQqypz9-yPyCAC5v4cAzouqjsMqyA"

# Function for /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_msg = (
        "💀 *Welcome to Insta Reset Bot!* 💀\n\n"
        "🚀 *Need a password reset?* Just send me your Instagram username or email, and I'll request a reset for you.\n\n"
        "🔹 *Fast, Secure & Hassle-Free!*\n"
        "🔹 *Stay in control of your account.*\n\n"
        "📌 *Created by:* @spokycap | @Cyberjurks"
    )
    await update.message.reply_text(welcome_msg, parse_mode="MarkdownV2")

# 🔹 Function to handle password reset request
async def send_reset_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()  # Get user input (username/email)

    url = "https://i.instagram.com/api/v1/accounts/send_password_reset/"  # IG password reset API

    headers = {
        "User-Agent": "Mozilla/5.0",
        "x-csrftoken": "vEG96oJnlEsyUWNS53bHLkVTMFYQKCBV",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {"username_or_email": user_input}  # Fixed parameter name

    try:
        response = requests.post(url, headers=headers, data=data)

        # Try to parse response as JSON
        try:
            response_json = response.json()
            formatted_json = json.dumps(response_json, indent=2)

            # Escape special characters for MarkdownV2 (double backslashes)
            escape_chars = r"\._{}[]()#+-=|!`>"
            for char in escape_chars:
                formatted_json = formatted_json.replace(char, f"\\{char}")

            formatted_response = f"📩 *Instagram Response:*\n```\n{formatted_json}\n```"

        except json.JSONDecodeError:
            formatted_response = "❌ *Instagram Response:* Unable to parse JSON response."

        await update.message.reply_text(formatted_response, parse_mode="MarkdownV2")

    except requests.exceptions.RequestException as e:
        logger.error(f"Network error: {e}")
        await update.message.reply_text("❌ *Error:* Unable to reach Instagram servers.")

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await update.message.reply_text("❌ An unexpected error occurred.")

# 🔹 Start the Telegram bot
def main():
    # Prevent multiple bot instances from running
    import os
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))  # Handle /start command
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_reset_request))  # Handle messages

    # Start the bot
    logger.info("✅ Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)  # Ensure all updates are received

if __name__ == "__main__":
    main()
