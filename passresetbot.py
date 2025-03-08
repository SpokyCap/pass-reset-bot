import os
import uuid
import string
import random
import requests
from cfonts import render
import pyfiglet
import py_compile
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Telegram Bot Token
TOKEN = "7710265909:AAG9zB5VHfSByeTVIqbSPL-EkpFcgpoj574"

R = "\033[1;31m"
G = "\033[1;32m"
B = "\033[0;94m"
Y = "\033[1;33m"

# --- Flick Tools Class adapted for Telegram Bot ---
class FlickToolsBot:
    def __init__(self, update, context, target, input_type=None):
        self.update = update
        self.context = context
        self.target = target
        self.input_type = input_type # 'email' or 'username' or None (auto-detect)
        self.data = {}

    def process_target(self):
        if self.target[0] == "@":
            self.send_message("[♥︎] 𝗘𝗡𝗧𝗘𝗥 𝗧𝗛𝗘 𝗨𝗦𝗘𝗥𝗡𝗔𝗠𝗘 𝗪𝗜𝗧HOUT '@'")
            return False
        if self.input_type == 'email' or (self.input_type is None and "@" in self.target): # Check input_type or auto-detect if None
            self.data = {
                "_csrftoken": "".join(
                    random.choices(
                        string.ascii_lowercase + string.ascii_uppercase + string.digits, k=32
                    )
                ),
                "user_email": self.target,
                "guid": uuid.uuid4(),
                "device_id": uuid.uuid4(),
            }
        elif self.input_type == 'username' or (self.input_type is None and "@" not in self.target): # Check input_type or auto-detect if None
            self.data = {
                "_csrftoken": "".join(
                    random.choices(
                        string.ascii_lowercase + string.ascii_uppercase + string.digits, k=32
                    )
                ),
                "username": self.target,
                "guid": uuid.uuid4(),
                "device_id": uuid.uuid4(),
            }
        else:
            self.send_message("Invalid input type. Please use /email or /username command before entering the ID.")
            return False
        return True

    def send_password_reset(self):
        if not self.process_target():
            return

        head = {
            "user-agent": f"Instagram 150.0.0.0.000 Android (29/10; 300dpi; 720x1440; {''.join(random.choices(string.ascii_lowercase+string.digits, k=16))}/{''.join(random.choices(string.ascii_lowercase+string.digits, k=16))}; {''.join(random.choices(string.ascii_lowercase+string.digits, k=16))}; {''.join(random.choices(string.ascii_lowercase+string.digits, k=16))}; {''.join(random.choices(string.ascii_lowercase+string.digits, k=16))}; en_GB;)"
        }
        try:
            req = requests.post(
                "https://i.instagram.com/api/v1/accounts/send_password_reset/",
                headers=head,
                data=self.data,
                timeout=10
            )
            req.raise_for_status()

            if "obfuscated_email" in req.text:
                self.send_message(f"[+] Reset request sent successfully for: {self.target}\n[+] Response: {req.text}")
            else:
                self.send_message(f"[-] Reset request failed for: {self.target}\n[-] Response: {req.text}")

        except requests.exceptions.RequestException as e:
            self.send_message(f"[-] An error occurred while sending the reset request for: {self.target}")
            self.send_message(f"[-] Error details: {e}")

    def send_message(self, text):
        self.update.message.reply_text(text)


# --- Telegram Bot Handlers ---
def start(update, context):
    flick_tools_banner = render('Flick Tools', colors=['white', 'cyan'], align='center')
    update.message.reply_text(f"```\n{flick_tools_banner}\n```", parse_mode=telegram.ParseMode.MARKDOWN)
    update.message.reply_text("Pass Reset Tool By : SpokyCap\nThis File Can Reset Hotmail Account [ 70% ]\n\nTo send a reset request, use:\n\n* `/email your_email@example.com`  (for email reset)\n* `/username yourusername` (for username reset)\n\nAlternatively, you can just enter your email or username directly after sending /start.")


def handle_email(update, context):
    if context.args:
        email_address = context.args[0] # Get email from command arguments
        bot_instance = FlickToolsBot(update, context, email_address, input_type='email')
        bot_instance.send_password_reset()
    else:
        update.message.reply_text("Please provide an email address after the /email command. For example: `/email test@example.com`")

def handle_username(update, context):
    if context.args:
        username = context.args[0] # Get username from command arguments
        bot_instance = FlickToolsBot(update, context, username, input_type='username')
        bot_instance.send_password_reset()
    else:
        update.message.reply_text("Please provide a username after the /username command. For example: `/username testuser`")


def handle_message(update, context):
    user_input = update.message.text
    # Assume it's email or username if no command is used, and let the bot auto-detect
    bot_instance = FlickToolsBot(update, context, user_input) # input_type is None for auto-detect
    bot_instance.send_password_reset()


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("email", handle_email, pass_args=True)) # Add handler for /email command
    dp.add_handler(CommandHandler("username", handle_username, pass_args=True)) # Add handler for /username command
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    print("Telegram Bot started...")
    main()
