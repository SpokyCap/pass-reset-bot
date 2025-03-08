import os
import uuid
import string
import random
import requests
import asyncio
from cfonts import render
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

# ⚠️ IMPORTANT: Replace with your actual Telegram Bot Token from BotFather! ⚠️
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

# Render a stylish banner (purely visual, can be removed if not needed)
banner = render('SpokyCap Tools', colors=['red', 'cyan'], align='center')
print(banner)
print("\U0001F511 Pass Reset Tool By: SpokyCap 🎯\n⚡ Sends Instagram Password Reset Links ⚡\n")

def generate_reset_data(target):
    """Generate reset request payload for Instagram."""
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
    """Send password reset request to Instagram."""
    headers = {
        "User-Agent": f"Instagram 150.0.0.0.000 Android (29/10; 300dpi; 720x1440; {''.join(random.choices(string.ascii_lowercase+string.digits, k=16))}; en_GB;)"
    }
    data = generate_reset_data(target)
    try:
        response = requests.post("https://i.instagram.com/api/v1/accounts/send_password_reset/", headers=headers, data=data, timeout=10) # Added timeout
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        if "obfuscated_email" in response.text:
            return f"✅ [+] Success: {response.text}"
        else:
            return f"❌ [-] Failed: {response.text}"

    except requests.exceptions.RequestException as e: # Catch network errors
        return f"❌ [-] Failed with error: {e}"

async def reset_command(update: Update, context: CallbackContext) -> None:
    """Handle the /reset command in Telegram."""
    if not context.args:
        await update.message.reply_text("⚠️ Usage: /reset <email/username>")
        return
    target = context.args[0]
    if target.startswith("@"):
        await update.message.reply_text("🚨 [!] Enter the username without '@' symbol.")
        return

    await update.message.reply_text(f"⏳ Sending password reset link for: {target}...") # Added processing message
    result = await send_password_reset(target)
    await update.message.reply_text(result)

async def main():
    """Start and run the Telegram bot."""
    if TELEGRAM_BOT_TOKEN == "7710265909:AAG9zB5VHfSByeTVIqbSPL-EkpFcgpoj574": # Check if token was replaced
        print("❌ Error: Bot token is missing! You MUST replace 'YOUR_TELEGRAM_BOT_TOKEN' with your actual bot token.")
        return

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("reset", reset_command))

    print("🤖 Telegram bot is now running! Send /reset <email/username> in Telegram to use it.")
    await app.run_polling()

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()

    try:
        asyncio.run(main()) # Use asyncio.run to start the async main function
    except KeyboardInterrupt:
        print("Bot stopped manually.") # Handle manual bot stopping
    except Exception as e:
        print(f"Bot failed to start due to error: {e}") # Catch other startup errors
