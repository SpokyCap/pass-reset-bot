import os
import uuid
import string
import random
import requests
from cfonts import render
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# 🔑 Insert your Telegram Bot Token here (Replace with your actual token)
TELEGRAM_BOT_TOKEN = "7710265909:AAG9zB5VHfSByeTVIqbSPL-EkpFcgpoj574"

# Render a stylish banner
banner = render('SpokyCap Tools', colors=['red', 'cyan'], align='center')
print(banner)
print("🔑 Pass Reset Tool By: SpokyCap 🎭\n⚡ Sends Instagram Password Reset Links ⚡\n")

def generate_reset_data(target):
    """Generate reset request payload."""
    data = {
        "_csrftoken": "".join(random.choices(string.ascii_letters + string.digits, k=32)),
        "guid": str(uuid.uuid4()),
        "device_id": str(uuid.uuid4())
    }
    if "@" in target:
        data["user_email"] = target
    else:
        data["username"] = target
    return data

def send_password_reset(target):
    """Send password reset request."""
    headers = {
        "User-Agent": f"Instagram 150.0.0.0.000 Android (29/10; 300dpi; 720x1440; {''.join(random.choices(string.ascii_lowercase+string.digits, k=16))}; en_GB;)"
    }
    data = generate_reset_data(target)
    response = requests.post("https://i.instagram.com/api/v1/accounts/send_password_reset/", headers=headers, data=data)
    
    if "obfuscated_email" in response.text:
        return f"✅ [+] Success: {response.text}"
    else:
        return f"❌ [-] Failed: {response.text}"

def reset_command(update: Update, context: CallbackContext) -> None:
    """Handle /reset command in Telegram."""
    if not context.args:
        update.message.reply_text("⚠️ Usage: /reset <email/username>")
        return
    target = context.args[0]
    if target.startswith("@"):  # Ensure username format is correct
        update.message.reply_text("🚨 [!] Enter the username without '@'")
        return
    result = send_password_reset(target)
    update.message.reply_text(result)

def main():
    """Start the Telegram bot."""
    if not TELEGRAM_BOT_TOKEN:
        print("❌ Error: Bot token is missing. Make sure it's set in the script.")
        return
    
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("reset", reset_command))
    
    print("🤖 Bot is now running! Send /reset <email/username> in Telegram to use it.")
    
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
