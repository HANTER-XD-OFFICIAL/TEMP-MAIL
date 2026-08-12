import telebot
import requests
import random
import string
import time
from flask import Flask
from threading import Thread
from telebot import types

# --- Configuration ---
BOT_TOKEN = '8821453331:AAHA_14xkD-f_OjvCUlY5CQ5iVYxIENBPB4'
DEVELOPER_USERNAME = 'HANTER_XD_OFFICIAL'
API_URL = "https://api.mail.tm"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

# --- Keep Alive Server for Render ---
@app.route('/')
def home():
    return "Temp Mail Pro is Running Successfully!"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- Mail.tm API Functions ---
def get_domains():
    try:
        res = requests.get(f"{API_URL}/domains")
        return res.json()['hydra:member'][0]['domain']
    except:
        return "mail.tm"

def create_account():
    domain = get_domains()
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    email = f"{username}@{domain}"
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    
    data = {"address": email, "password": password}
    res = requests.post(f"{API_URL}/accounts", json=data)
    if res.status_code == 201:
        return email, password
    return None, None

def get_token(email, password):
    data = {"address": email, "password": password}
    res = requests.post(f"{API_URL}/token", json=data)
    if res.status_code == 200:
        return res.json()['token']
    return None

# --- Telegram Bot Handlers ---

@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton("📧 Generate Pro Email", callback_data="gen_email")
    markup.add(btn)
    
    welcome_text = (
        f"✨ *Welcome to Temp Mail Pro* ✨\n\n"
        f"Protect your personal inbox from spam and hackers by using our high-speed disposable email service.\n\n"
        f"🚀 *Service Status:* Online\n"
        f"🛡️ *Privacy:* Encrypted\n"
        f"👨‍💻 *Developer:* @{DEVELOPER_USERNAME}\n\n"
        f"Click the button below to create your temporary inbox!"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "gen_email")
def gen_email_callback(call):
    bot.answer_callback_query(call.id, "Generating your secure email...")
    email, password = create_account()
    
    if email:
        markup = types.InlineKeyboardMarkup(row_width=1)
        # Data format for callback: chk|email|password
        refresh_data = f"chk|{email}|{password}"
        
        refresh_btn = types.InlineKeyboardButton("🔄 Refresh Inbox", callback_data=refresh_data)
        markup.add(refresh_btn)
        
        email_text = (
            f"📥 *Your Professional Temp Email:*\n"
            f"`{email}`\n\n"
            f"🔑 *Password:* `{password}`\n\n"
            f"⚠️ *Note:* Copy your email and use it. Click the button below to check for incoming messages."
        )
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=email_text,
            parse_mode="Markdown",
            reply_markup=markup
        )
    else:
        bot.send_message(call.message.chat.id, "❌ System Error: Unable to create account. Please try again.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("chk|"))
def check_inbox(call):
    _, email, password = call.data.split("|")
    bot.answer_callback_query(call.id, "Checking inbox...")
    
    token = get_token(email, password)
    if not token:
        bot.send_message(call.message.chat.id, "❌ Error: Session expired. Please generate a new email.")
        return

    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(f"{API_URL}/messages", headers=headers).json()
    messages = res.get('hydra:member', [])

    if not messages:
        bot.answer_callback_query(call.id, "📭 Inbox is empty. Try again in a moment.", show_alert=True)
    else:
        inbox_text = f"📥 *Recent Messages for:* `{email}`\n\n"
        for msg in messages[:5]:
            msg_id = msg['id']
            # Fetch detailed message content
            m_res = requests.get(f"{API_URL}/messages/{msg_id}", headers=headers).json()
            inbox_text += f"📧 *From:* {msg['from']['address']}\n"
            inbox_text += f"📝 *Subject:* {msg['subject']}\n"
            inbox_text += f"📖 *Body:* {m_res.get('text', 'No content')[:300]}...\n"
            inbox_text += "----------------------------------\n"
        
        bot.send_message(call.message.chat.id, inbox_text, parse_mode="Markdown")

# --- Run Bot ---
if __name__ == "__main__":
    keep_alive()
    print("Temp Mail Pro is now Online!")
    while True:
        try:
            bot.infinity_polling(timeout=20, long_polling_timeout=10)
        except Exception as e:
            print(f"Connection Error: {e}")
            time.sleep(5)
