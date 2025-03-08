import os
import uuid
import string
import random
import requests
import asyncio  # ADDED: Import asyncio library
from cfonts import render
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

# Telegram Bot Token (Add your bot token here)
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN" # Replace with your actual bot token

# Render a stylish banner
banner = render('SpokyCap Tools', colors=['red', 'cyan'], align='center')
print(banner)
print("\U0001F511 Pass Reset Tool By: SpokyCap 🎯\n⚡ Sends Instagram Password Reset Links ⚡\n")

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

async def send_password_reset(target):
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

async def reset_command(update: Update, context: CallbackContext) -> None:
    """Handle /reset command in Telegram."""
    if not context.args:
        await update.message.reply_text("⚠️ Usage: /reset <email/username>")
        return
    target = context.args[0]
    if target.startswith("@"):  # Ensure username format is correct
        await update.message.reply_text("🚨 [!] Enter the username without '@'")
        return
    result = await send_password_reset(target)
    await update.message.reply_text(result)

async def main():
    """Start the Telegram bot."""
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN": # Check if token is actually set
        print("❌ Error: Bot token is missing. Please replace 'YOUR_TELEGRAM_BOT_TOKEN' with your actual bot token.")
        return

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("reset", reset_command))

    print("🤖 Bot is now running! Send /reset <email/username> in Telegram to use it.")

    await app.run_polling()

if __name__ == "__main__":
    import nest_asyncio  # 🔥 Fix for nested event loops in Render
    nest_asyncio.apply()  # ✅ Allows reusing the existing event loop

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())  # ✅ Correct way to run async in Render
