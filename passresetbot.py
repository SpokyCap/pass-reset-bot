import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Enable logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🔹 Replace this with your Telegram bot token
TELEGRAM_BOT_TOKEN = "7544051823:AAGWFsIQqypz9-yPyCAC5v4cAzouqjsMqyA"

# 🔹 Function for /start command
async def start(update: Update, context: CallbackContext):
    welcome_msg = (
        "🤖 Welcome to the Insta Reset Bot!\n\n"
        "🔹 Send me your Instagram username/email, and I'll request a password reset for you.\n"
        "           ~By @spokycap | @Cyberjurks\n\n "
    )
    await update.message.reply_text(welcome_msg)

# 🔹 Function to handle password reset request
async def send_reset_request(update: Update, context: CallbackContext):
    user_input = update.message.text.strip()  # Get user input (username/email)
    
    url = "https://i.instagram.com/api/v1/accounts/send_password_reset/"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "x-csrftoken": "vEG96oJnlEsyUWNS53bHLkVTMFYQKCBV"
    }
    
    data = {"user_email": user_input}

    try:
        response_json = response.json()  # Convert response to JSON

        if response_json.get("status") == "ok":
            obfuscated_email = response_json.get("obfuscated_email", "Unknown")
            msg = f"📩 Password reset link sent to: `{obfuscated_email}`"
        else:
            msg = "❌ Failed to send password reset request. Try again later."

        await update.message.reply_text(msg, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Error sending request: {e}")
        await update.message.reply_text("❌ An error occurred while processing your request.")

# 🔹 Start the Telegram bot
def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))  
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_reset_request))  

    # Start the bot
    logger.info("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
