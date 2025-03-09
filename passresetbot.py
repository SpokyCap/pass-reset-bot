import os
import subprocess
import sys
import logging

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

# 🔹 Logging setup
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

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
    
    try:
        # Send request
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        
        # Send the response back to Telegram
        await update.message.reply_text(f"📩 Instagram Response:\n{response.text}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending reset request: {e}")
        await update.message.reply_text("⚠️ Failed to send reset request. Please try again later.")

# 🔹 Start the Telegram bot
async def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))  # Handle /start command
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_reset_request))  # Handle messages

    # Check if running on Railway
    if "RAILWAY_STATIC_URL" in os.environ:
        PORT = int(os.environ.get("PORT", 8443))
        WEBHOOK_URL = f"https://{os.environ['RAILWAY_STATIC_URL']}/{TELEGRAM_BOT_TOKEN}"
        print(f"Starting bot with webhook at {WEBHOOK_URL}...")
        await app.bot.set_webhook(WEBHOOK_URL)
        app.run_webhook(listen="0.0.0.0", port=PORT, url_path=TELEGRAM_BOT_TOKEN)
    else:
        print("Starting bot with polling...")
        app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
