import telebot
import requests as C
import re
import json
from uuid import uuid4
import os
from flask import Flask, request

# Get BOT_TOKEN from environment variables
BOT_TOKEN = os.environ.get("7710265909:AAG9zB5VHfSByeTVIqbSPL-EkpFcgpoj574")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set.")

bot = telebot.TeleBot(BOT_TOKEN)
server = Flask(__name__)

@server.route(f"/{BOT_TOKEN}", methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{BOT_TOKEN}")
    return "!", 200

# Your bot's message handler
@bot.message_handler(func=lambda message: True)
def handle_instagram_reset(message):
    # Your code here
    bot.reply_to(message, "message Recieved")

# Your X, Y, and Z functions remain the same
def X(email_or_username):
    # ... (Your X function code) ...
    pass

def Y(response_text):
    # ... (Your Y function code) ...
    pass

def Z(username):
    # ... (Your Z function code) ...
    pass

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=10000)
