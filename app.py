import telebot
import requests
import random
import string
import time
from flask import Flask
from threading import Thread
from telebot import types

# --- কনফিগারেশন ---
BOT_TOKEN = 'আপনার_বট_টোকেন_এখানে'  # @BotFather থেকে পাওয়া টোকেন দিন
DEVELOPER_USERNAME = 'আপনার_ইউজারনেম' # এখানে @ ছাড়া আপনার নিজের ইউজারনেম দিন (উদা: 'Hanter_XD')
bot = telebot.TeleBot(BOT_TOKEN)

# --- Keep Alive Server (Render-এর জন্য) ---
app = Flask('')

@app.route('/')
def home():
    return "Temp Mail Pro is Running!"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- টেম্প ইমেইল ফাংশনস ---
def generate_email():
    domain = ["1secmail.com", "1secmail.net", "1secmail.org"]
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    email = f"{username}@{random.choice(domain)}"
    return email

# --- বট হ্যান্ডলারস ---
@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("📧 Generate New Email", callback_data="gen_email")
    markup.add(btn1)
    
    welcome_text = (
        f"🚀 *Welcome to Temp Mail Pro!*\\n\\n"
        f"Protect your privacy with instant disposable emails.\\n\\n"
        f"✅ Instant temp emails\\n"
        f"✅ Receive OTPs & verification codes\\n"
        f"✅ 100% Secure & Anonymous\\n\\n"
        f"👨‍💻 Developed by: @{DEVELOPER_USERNAME}\\n\\n"
        f"Click the button below to get your email! ✨"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "gen_email")
def gen_callback(call):
    email = generate_email()
    user_id = call.from_user.id
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    refresh_btn = types.InlineKeyboardButton("🔄 Refresh Inbox", callback_data=f"check_{email}")
    new_btn = types.InlineKeyboardButton("🆕 New Email", callback_data="gen_email")
    markup.add(refresh_btn, new_btn)
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"📧 *Your Temporary Email:*\\n`{email}`\\n\\n"
             f"Copy this email and use it anywhere. Click 'Refresh' to see your messages! 📥",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("check_"))
def check_inbox(call):
    email = call.data.split("_")[1]
    user, domain = email.split("@")
    
    # 1secmail API থেকে ইনবক্স চেক করা
    api_url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={user}&domain={domain}"
    response = requests.get(api_url).json()
    
    if not response:
        bot.answer_callback_query(call.id, "📭 No messages yet. Please wait or resend.")
    else:
        msg_list = "📥 *Recent Messages:*\\n\\n"
        for msg in response[:3]: # শেষ ৩টি মেসেজ দেখাবে
            msg_list += f"📩 *From:* {msg['from']}\\n"
            msg_list += f"📝 *Subject:* {msg['subject']}\\n"
            msg_list += f"📅 *Date:* {msg['date']}\\n"
            msg_list += "----------------------\\n"
        
        bot.send_message(call.message.chat.id, msg_list, parse_mode="Markdown")
        bot.answer_callback_query(call.id, "Messages loaded!")

# --- মেইন ফাংশন ---
if __name__ == "__main__":
    keep_alive() # রেন্ডার সার্ভার চালু হবে
    print(f"Bot started by @{DEVELOPER_USERNAME}")
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
