import telebot
import requests as C
import re
import json
from uuid import uuid4
import os
from flask import Flask, request

# Get BOT_TOKEN from environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
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


@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        bot.reply_to(message, "🌟 Hi! 🌟\n\nSend me an Instagram username or email to attempt a password reset and retrieve the masked email!")
    except Exception as e:
        print(f"BOT LOG: Error in /start handler: {e}")


# Function to send password reset request
def X(email_or_username):
    url = 'https://www.instagram.com/accounts/account_recovery_send_ajax/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://www.instagram.com/accounts/password/reset/',
        'X-CSRFToken': 'missing'  # Replace with the actual CSRF token
    }
    data = {'email_or_username': email_or_username, 'recaptcha_challenge_field': ''}
    print(f"BOT LOG: Sending request to {url}")
    print(f"BOT LOG: Headers: {headers}")
    print(f"BOT LOG: Data: {data}")
    response = C.post(url, headers=headers, data=data)
    print(f"BOT LOG: Response status code: {response.status_code}")
    print(f"BOT LOG: Response text: {response.text}")
    return response


# Function to extract masked email from response
def Y(response_text):
    match = re.search(r"We sent an email to <b>(.*?)</b>", response_text)
    if match:
        return match.group(1)  # Returns masked email like 's******p@gmail.com'
    return None  # If no masked email found


# Function to retrieve masked email using Instagram API
def Z(username):
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip',
        'accept-language': 'en-US,en;q=0.5',
        'referer': f"https://www.instagram.com/{username}",
        'x-ig-app-id': '936619743392459',
        'x-requested-with': 'XMLHttpRequest'
    }

    try:
        print(f"BOT LOG: Sending request to {url}")
        print(f"BOT LOG: Headers: {headers}")
        response = C.get(url, headers=headers).json()
        print(f"BOT LOG: Response: {response}")
        user_id = response['data']['user']['id']
    except Exception as e:
        print(f"BOT LOG: Failed to retrieve user ID - {e}")
        return None

    reset_url = 'https://i.instagram.com/api/v1/accounts/send_password_reset/'
    reset_headers = {
        'User-Agent': 'Instagram 6.12.1 Android',
        'X-IG-Connection-Type': 'MOBILE(LTE)',
        'Accept-Encoding': 'gzip'
    }
    reset_data = {'user_id': user_id, 'device_id': str(uuid4())}

    try:
        print(f"BOT LOG: Sending request to {reset_url}")
        print(f"BOT LOG: Headers: {reset_headers}")
        print(f"BOT LOG: Data: {reset_data}")
        reset_response = C.post(reset_url, headers=reset_headers, data=reset_data).json()
        print(f"BOT LOG: Response: {reset_response}")
        return reset_response.get('obfuscated_email')
    except Exception as e:
        print(f"BOT LOG: Failed to send password reset - {e}")
        return None


@bot.message_handler(func=lambda message: True)
def handle_instagram_reset(message):
    print("General message handler triggered")  # Log message handler trigger
    username_or_email = message.text.strip()
    response = X(username_or_email)

    if response.status_code == 200:
        extracted_email = Y(response.text)
        retrieved_email = Z(username_or_email)

        if extracted_email:
            try:
                bot.reply_to(message, f"✅ Reset sent to {extracted_email}")
            except Exception as e:
                print(f"BOT LOG: Failed to send Telegram reply: {e}")
            print(f"BOT LOG: Reset sent to {extracted_email}")
        elif retrieved_email:
            try:
                bot.reply_to(message, f"✅ Reset sent to {retrieved_email}")
            except Exception as e:
                print(f"BOT LOG: Failed to send Telegram reply: {e}")
            print(f"BOT LOG: Reset sent to {retrieved_email}")
        else:
            try:
                bot.reply_to(message, f"✅ Reset sent to {username_or_email}")
            except Exception as e:
                print(f"BOT LOG: Failed to send Telegram reply: {e}")
            print(f"BOT LOG: Reset sent to {username_or_email}")
    else:
        try:
            bot.reply_to(message, f"❌ Failed to send reset to {username_or_email}")
        except Exception as e:
            print(f"BOT LOG: Failed to send Telegram reply: {e}")
        print(f"BOT LOG: Failed to send reset to {username_or_email}")


if __name__ == "__main__":
    from waitress import serve
    serve(server, host="0.0.0.0", port=10000)
