import os
import requests
import random
import string
import telebot
from flask import Flask, render_template
from threading import Thread
from telebot import types

# --- কনফিগারেশন ---
TOKEN = '8821453331:AAGG0KnJNrDT-nyKMAaa2xpa_lrp90nbK-I'
ADMIN_ID = "HANTER_XD_OFFICIAL" 
PORTFOLIO_LINK = "https://hanter-xd-official.github.io/PORTFOLIO/" # আপনার পোর্টফোলিও লিঙ্ক
API_BASE = "https://api.mail.tm"

app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)

# সেশন স্টোরেজ
user_data = {}

def generate_account():
    try:
        domains = requests.get(f"{API_BASE}/domains").json()
        domain = domains['hydra:member'][0]['domain']
        user = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        email = f"{user}@{domain}"
        
        res = requests.post(f"{API_BASE}/accounts", json={"address": email, "password": password})
        if res.status_code == 201:
            token_res = requests.post(f"{API_BASE}/token", json={"address": email, "password": password}).json()
            return email, password, token_res['token']
        return None, None, None
    except:
        return None, None, None

def get_messages(token):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        res = requests.get(f"{API_BASE}/messages", headers=headers).json()
        return res.get('hydra:member', [])
    except:
        return []

# --- বোট ফাংশনস ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_msg = (
        f"👋 *Hi {message.from_user.first_name}!*\n\n"
        f"Welcome to *Temp Mail Pro Bot* 📧\n"
        f"আপনার প্রাইভেসি রক্ষা করতে ডিসপোজেবল ইমেইল ব্যবহার করুন।\n\n"
        f"🛠 *Developed by:* @{ADMIN_ID}\n"
        f"✨ *Status:* Online & Fast"
    )
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("📧 Generate Mail", callback_data="gen_mail")
    btn2 = types.InlineKeyboardButton("📢 Support", url=f"https://t.me/{ADMIN_ID}")
    # এখানে আপনার পোর্টফোলিও লিঙ্ক সেট করা হয়েছে
    btn3 = types.InlineKeyboardButton("🌐 Visit Website", url=PORTFOLIO_LINK) 
    
    markup.add(btn1)
    markup.add(btn2, btn3)

    bot.send_message(message.chat.id, welcome_msg, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "gen_mail":
        bot.answer_callback_query(call.id, "Generating...")
        email, password, token = generate_account()
        
        if email:
            user_data[call.message.chat.id] = {'email': email, 'token': token, 'pass': password}
            
            res_msg = (
                f"📧 *Your Temp Email:*\n`{email}`\n\n"
                f"🔑 *Password:* `{password}`\n\n"
                f"⚠️ *Note:* এই ইমেইলটি সাময়িক সময়ের জন্য।\n"
                f"--- ✨ Powered by @{ADMIN_ID} ---"
            )
            
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("📥 Refresh Inbox", callback_data="refresh_inbox"))
            markup.add(types.InlineKeyboardButton("🗑 Generate New", callback_data="gen_mail"))
            
            bot.edit_message_text(res_msg, call.message.chat.id, call.message.message_id, 
                                 parse_mode="Markdown", reply_markup=markup)
        else:
            bot.send_message(call.message.chat.id, "❌ Error creating email. Try again.")

    elif call.data == "refresh_inbox":
        user = user_data.get(call.message.chat.id)
        if not user:
            bot.answer_callback_query(call.id, "No active session!")
            return

        bot.answer_callback_query(call.id, "Checking for new mails...")
        msgs = get_messages(user['token'])
        
        if not msgs:
            bot.send_message(call.message.chat.id, "📭 ইনবক্স এখনো খালি।")
        else:
            for m in msgs[:3]:
                sender = m['from']['address']
                subject = m['subject'] or "No Subject"
                bot.send_message(call.message.chat.id, 
                                f"📩 *New Mail!*\n\n*From:* {sender}\n*Subject:* {subject}\n\n"
                                f"বিস্তারিত জানতে ইনবক্স রিফ্রেশ করুন।", 
                                parse_mode="Markdown")

# --- ওয়েব সার্ভার ---

@app.route('/')
def index():
    return render_template('index.html')

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

if __name__ == "__main__":
    t = Thread(target=run_flask)
    t.start()
    print(f"Bot started by @{ADMIN_ID}")
    bot.infinity_polling()
