import os
import asyncio
import logging
import requests
import random
import time
import json
import uuid
from telegram import Update, error
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Enable logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram bot token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7544051823:AAGWFsIQqypz9-yPyCAC5v4cAzouqjsMqyA")

# Simulated "devices" with unique headers, cookies, and App-IDs
DEVICES = [
    {
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "x-csrftoken": "X7kP9mLqzialQA7z96AMiyAKLMBWpqVj",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://www.instagram.com",
            "Referer": "https://www.instagram.com/accounts/password/reset/",
            "X-Requested-With": "XMLHttpRequest",
            "X-IG-App-ID": "1217981644879628",
            "X-IG-Connection-Type": "WIFI",
            "X-IG-Capabilities": "3brTvw==",
            "X-Pigeon-Session-Id": str(uuid.uuid4()),
            "X-IG-Bandwidth-Speed-KBPS": "1500.000",
            "X-IG-Bandwidth-TotalBytes-B": "300000",
        },
        "cookies": {
            "csrftoken": "X7kP9mLqzialQA7z96AMiyAKLMBWpqVj",
            "sessionid": "",
            "mid": "Z1aB2cD3eF4gH5iJ6kL7mN8oP9qR",
            "ig_did": "123E4567-E89B-12D3-A456-426614174000",
            "rur": "ASH",
            "ig_nrcb": "1",
        },
        "last_used": 0,
        "name": "Windows Chrome"
    },
    {
        "headers": {
            "User-Agent": "Instagram 100.0.0.17.129 (iPhone13,3; iOS 15_0; en_US; en-US; scale=3.00; 1170x2532; 161478664)",
            "x-csrftoken": "P4nM8kJqzialQA7z96AMiyAKLMBWpqVj",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://www.instagram.com",
            "Referer": "https://www.instagram.com/accounts/password/reset/",
            "X-Requested-With": "XMLHttpRequest",
            "X-IG-App-ID": "567067343352427",
            "X-IG-Connection-Type": "WIFI",
            "X-IG-Capabilities": "3brTvx8=",
            "X-Pigeon-Session-Id": str(uuid.uuid4()),
            "X-IG-Bandwidth-Speed-KBPS": "3200.000",
            "X-IG-Bandwidth-TotalBytes-B": "600000",
        },
        "cookies": {
            "csrftoken": "P4nM8kJqzialQA7z96AMiyAKLMBWpqVj",
            "sessionid": "",
            "mid": "Q9wX8vU7tS6rP5oN4mL3kJ2iH1gF",
            "ig_did": "987F6543-21AB-12C3-D456-789123456789",
            "ds_user_id": "fakeuser987654",
            "rur": "PRN",
        },
        "last_used": 0,
        "name": "iPhone Safari"
    },
    {
        "headers": {
            "User-Agent": "Instagram 194.0.0.36.172 Android (30/11; 440dpi; 1080x2340; samsung; SM-G991B; exynos2100; en_US; 293092486)",
            "x-csrftoken": "K2xL7mNqzialQA7z96AMiyAKLMBWpqVj",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://www.instagram.com",
            "Referer": "https://www.instagram.com/accounts/password/reset/",
            "X-Requested-With": "XMLHttpRequest",
            "X-IG-App-ID": "124024574287414",
            "X-IG-Connection-Type": "MOBILE(LTE)",
            "X-IG-Capabilities": "3brTvwM=",
            "X-Pigeon-Session-Id": str(uuid.uuid4()),
            "X-IG-Bandwidth-Speed-KBPS": "1800.000",
            "X-IG-Bandwidth-TotalBytes-B": "450000",
        },
        "cookies": {
            "csrftoken": "K2xL7mNqzialQA7z96AMiyAKLMBWpqVj",
            "sessionid": "",
            "mid": "R5tY4uI3oP2nM1lK0jH9gF8eD7cB",
            "ig_did": "ABC12345-6789-0DEF-1234-56789ABCDEF0",
            "ig_nrcb": "1",
            "ds_user_id": "fakeandroid54321",
        },
        "last_used": 0,
        "name": "Android Chrome"
    }
]

# Request cooldown
REQUEST_COOLDOWN = 30  # 30 seconds minimum between requests per device

# Function for /start command
async def start(update: Update, context: CallbackContext):
    welcome_msg = (
        "🤖 Welcome to the Insta Reset Bot!\n\n"
        "🔹 Send me your Instagram username/email, and I'll request a password reset for you.\n"
        "           ~By @spokycap | @Cyberjurks\n\n"
    )
    await update.message.reply_text(welcome_msg)

# Function to handle incoming messages
async def send_reset_request(update: Update, context: CallbackContext):
    user_input = update.message.text.strip()  # Get user input (username/email)
    url = "https://i.instagram.com/api/v1/accounts/send_password_reset/"  # IG password reset API

    # Select the least recently used device
    available_devices = [d for d in DEVICES if time.time() - d["last_used"] >= REQUEST_COOLDOWN]
    if not available_devices:
        await update.message.reply_text("⏳ All devices are on cooldown. Try again in 30-60 seconds.")
        return
    
    device = random.choice(available_devices)
    device["last_used"] = time.time()
    logger.info(f"Activating device: {device['name']}")
    
    data = {"user_email": user_input}

    try:
        response = requests.post(
            url,
            headers=device["headers"],
            cookies=device["cookies"],
            data=data,
            timeout=10
        )
        if response.status_code == 429:
            await update.message.reply_text("⏳ Instagram rate limit hit. Please wait 5-10 minutes.")
        elif response.status_code == 200:
            try:
                response_data = response.json()
                obfuscated_email = response_data.get("obfuscated_email", "your email")
                await update.message.reply_text(f"📩 Success! Check {obfuscated_email} for the reset link.")
            except json.JSONDecodeError:
                await update.message.reply_text("📩 Success! Check your email for the reset link.")
        else:
            try:
                error_data = response.json()
                error_message = error_data.get("message", response.text)
                max_length = 4096 - len("❌ Instagram Error: ")
                if len(error_message) > max_length:
                    error_message = error_message[:max_length] + "..."
                await update.message.reply_text(f"❌ Instagram Error: {error_message}")
            except json.JSONDecodeError:
                error_message = response.text
                max_length = 4096 - len("❌ Instagram Error: ")
                if len(error_message) > max_length:
                    error_message = error_message[:max_length] + "..."
                await update.message.reply_text(f"❌ Instagram Error: {error_message}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error with {device['name']}: {e}")
        await update.message.reply_text("❌ An error occurred while processing your request.")

# Error handler for Telegram conflicts
async def error_handler(update: Update, context: CallbackContext):
    logger.error(f"Exception occurred: {context.error}")
    if isinstance(context.error, error.Conflict):
        await update.message.reply_text("⚠️ Bot conflict detected. Restarting in a moment...")
        time.sleep(5)
        raise context.error
    elif isinstance(context.error, error.BadRequest) and "Message is too long" in str(context.error):
        await update.message.reply_text("❌ Error: Response too long to send. Check logs for details.")
    else:
        await update.message.reply_text("❌ An unexpected error occurred.")

# Start the Telegram bot
async def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Disable webhook
    await app.bot.delete_webhook(drop_pending_updates=True)
    logger.info("Webhook disabled, starting polling...")

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_reset_request))
    app.add_error_handler(error_handler)

    # Start the bot
    logger.info("Bot is running...")
    await app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    # Use the existing event loop instead of asyncio.run()
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # If the loop is already running (e.g., in Railway), create a task
        task = loop.create_task(main())
        try:
            loop.run_until_complete(task)
        except KeyboardInterrupt:
            task.cancel()
            loop.run_until_complete(asyncio.gather(task, return_exceptions=True))
            loop.close()
    else:
        # If no loop is running, run it normally
        loop.run_until_complete(main())
