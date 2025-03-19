import os
import asyncio
import logging
import requests
import random
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram bot token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7544051823:AAGWFsIQqypz9-yPyCAC5v4cAzouqjsMqyA")

# Simulated "devices" with headers and cookies
DEVICES = [
    {
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "x-csrftoken": "vEG96oJnlEsyUWNS53bHLkVTMFYQKCBV",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "*/*",
            "Origin": "https://www.instagram.com",
            "Referer": "https://www.instagram.com/accounts/password/reset/",
            "X-Requested-With": "XMLHttpRequest",
        },
        "cookies": {
            "csrftoken": "vEG96oJnlEsyUWNS53bHLkVTMFYQKCBV",
            "sessionid": "",
            "mid": "random_mid_123",
            "ig_did": "fake_device_id_win_001"
        },
        "last_used": 0,
        "name": "Windows Chrome"
    },
    {
        "headers": {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
            "x-csrftoken": "vEG96oJnlEsyUWNS53bHLkVTMFYQKCBV",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "*/*",
            "Origin": "https://www.instagram.com",
            "Referer": "https://www.instagram.com/accounts/password/reset/",
            "X-Requested-With": "XMLHttpRequest",
        },
        "cookies": {
            "csrftoken": "vEG96oJnlEsyUWNS53bHLkVTMFYQKCBV",
            "sessionid": "",
            "mid": "random_mid_456",
            "ig_did": "fake_device_id_ios_002"
        },
        "last_used": 0,
        "name": "iPhone Safari"
    },
    {
        "headers": {
            "User-Agent": "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.91 Mobile Safari/537.36",
            "x-csrftoken": "vEG96oJnlEsyUWNS53bHLkVTMFYQKCBV",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "*/*",
            "Origin": "https://www.instagram.com",
            "Referer": "https://www.instagram.com/accounts/password/reset/",
            "X-Requested-With": "XMLHttpRequest",
        },
        "cookies": {
            "csrftoken": "vEG96oJnlEsyUWNS53bHLkVTMFYQKCBV",
            "sessionid": "",
            "mid": "random_mid_789",
            "ig_did": "fake_device_id_android_003"
        },
        "last_used": 0,
        "name": "Android Chrome"
    }
]

# Request queue and cooldown
REQUEST_COOLDOWN = 5  # 5 seconds minimum between requests per device
request_queue = asyncio.Queue()

# /start command
async def start(update: Update, context: CallbackContext):
    welcome_msg = (
        "🤖 Welcome to the Insta Reset Bot!\n\n"
        "🔹 Send me your Instagram username/email, and I'll request a password reset for you.\n"
        "           ~By @spokycap | @Cyberjurks\n\n"
    )
    await update.message.reply_text(welcome_msg)

# Process requests with device activation
async def process_requests():
    while True:
        user_input, update, context = await request_queue.get()
        url = "https://i.instagram.com/api/v1/accounts/send_password_reset/"
        
        # Select the least recently used device
        available_devices = [d for d in DEVICES if time.time() - d["last_used"] >= REQUEST_COOLDOWN]
        if not available_devices:
            await update.message.reply_text("⏳ All devices are on cooldown. Try again in a few seconds.")
            await request_queue.put((user_input, update, context))  # Re-queue
            await asyncio.sleep(1)
            continue
        
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
                await update.message.reply_text("⏳ Too many requests. Please wait and try again later.")
            elif response.status_code == 200:
                await update.message.reply_text("📩 Success! Check your email for the reset link.")
            else:
                await update.message.reply_text(f"📩 Instagram Response:\n{response.text}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error with {device['name']}: {e}")
            await update.message.reply_text("❌ An error occurred while processing your request.")
        
        # Random delay to simulate "power saving"
        await asyncio.sleep(REQUEST_COOLDOWN + random.uniform(0, 3))  # 5-8 seconds
        request_queue.task_done()

# Handle incoming messages
async def send_reset_request(update: Update, context: CallbackContext):
    user_input = update.message.text.strip()
    if request_queue.qsize() > 10:  # Limit queue size
        await update.message.reply_text("⏳ Bot is busy. Please try again in a minute.")
        return
    await request_queue.put((user_input, update, context))

# Main function (synchronous wrapper)
def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_reset_request))
    
    # Start the request processor task
    loop = asyncio.get_event_loop()
    loop.create_task(process_requests())
    
    logger.info("Bot is running...")
    app.run_polling()  # This runs the event loop

if __name__ == "__main__":
    main()  # Call synchronously, let run_polling handle the loop
