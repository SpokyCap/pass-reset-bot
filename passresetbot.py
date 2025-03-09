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
        "User-Agent": "Instagram 155.0.0.37.107 Android",  # More realistic user-agent
        "Accept": "*/*",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-IG-App-ID": "936619743392459",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    data = {"username_or_email": user_input}  # Fixed parameter name

    try:
        response = requests.post(url, headers=headers, data=data)
        
        # Log response for debugging
        logger.info(f"Instagram API Response: {response.text}")

        # Check for successful request
        if response.status_code == 200:
            response_json = response.json()
            if response_json.get("status") == "ok":
                obfuscated_email = response_json.get("obfuscated_email", "Unknown")
                msg = f"📩 Password reset link sent to: `{obfuscated_email}`"
            else:
                msg = "❌ Instagram did not accept the request. Try again later."
        else:
            msg = f"❌ Instagram API error (Status {response.status_code}): {response.text}"

        await update.message.reply_text(msg, parse_mode="Markdown")

    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        await update.message.reply_text(f"❌ Request error: {e}")

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await update.message.reply_text("❌ An unexpected error occurred.")

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
