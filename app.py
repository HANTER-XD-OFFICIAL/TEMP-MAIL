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
PORTFOLIO_LINK = "https://hanter-xd-official.github.io/PORTFOLIO/"
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

# --- ইমেইল জেনারেট করার ফাংশন ---
def process_gen_mail(chat_id):
    email, password, token = generate_account()
    if email:
        user_data[chat_id] = {'email': email, 'token': token, 'pass': password}
        res_msg = (
            f"✨ *Your Professional Temp Mail is Ready!*\n\n"
            f"📧 *Email:* `{email}`\n"
            f"🔑 *Password:* `{password}`\n\n"
            f"🛡️ *Security:* This email is private and temporary.\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 *Owner:* @{ADMIN_ID}"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📥 Refresh Inbox", callback_data="refresh_inbox"))
        markup.add(types.InlineKeyboardButton("🔄 Generate New", callback_data="gen_mail"))
        bot.send_message(chat_id, res_msg, parse_mode="Markdown", reply_markup=markup)
    else:
        bot.send_message(chat_id, "❌ Something went wrong. Try again.")

# --- প্রফেশনাল স্টার্ট হ্যান্ডলার ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    # সুন্দর করে সাজানো ওয়েলকাম টেক্সট
    welcome_text = (
        f"🌟 *Hi {message.from_user.first_name}! Welcome to Temp Mail Pro*\n\n"
        f"🔐 *Protect your privacy* by using a disposable email address for social media, "
        f"websites, and apps.\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👤 *Developer:* @{ADMIN_ID}\n"
        f"🚀 *Status:* System Online ✅\n"
        f"━━━━━━━━━━━━━━━━━━\n\n"
        f"👇 *নিচের বাটন থেকে আপনার ইমেইল তৈরি করুন:*"
    )
    
    # Inline Buttons (মেসেজের সাথে থাকা বাটন)
    inline_markup = types.InlineKeyboardMarkup(row_width=2)
    btn_gen = types.InlineKeyboardButton("📧 Generate Mail", callback_data="gen_mail")
    btn_web = types.InlineKeyboardButton("🌐 Visit Website", url=PORTFOLIO_LINK)
    btn_sup = types.InlineKeyboardButton("📢 Support", url=f"https://t.me/{ADMIN_ID}")
    
    # বাটনগুলো সাজানো
    inline_markup.add(btn_gen) # এটি একাই এক লাইনে থাকবে
    inline_markup.add(btn_web, btn_sup) # এই দুটি পাশাপাশি থাকবে

    # Reply Keyboard (নিচের স্থায়ী বাটন)
    reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    reply_markup.add("📧 Generate Email", "📥 Check Inbox")

    # একটি মেসেজেই সবকিছু পাঠানো
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=inline_markup)
    # রিপ্লাই কিবোর্ডটি অটোমেটিক সেট হয়ে যাবে
    bot.send_message(message.chat.id, "💡 *Quick Access Activated*", parse_mode="Markdown", reply_markup=reply_markup)

# --- কিবোর্ড মেসেজ হ্যান্ডলার ---

@bot.message_handler(func=lambda message: message.text == "📧 Generate Email")
def handle_gen_mail_msg(message):
    bot.send_message(message.chat.id, "⏳ *Generating your email...*", parse_mode="Markdown")
    process_gen_mail(message.chat.id)

@bot.message_handler(func=lambda message: message.text == "📥 Check Inbox")
def handle_check_inbox_msg(message):
    user = user_data.get(message.chat.id)
    if not user:
        bot.reply_to(message, "⚠️ Please generate an email first!")
        return
    
    bot.send_message(message.chat.id, "📥 *Checking inbox for new messages...*", parse_mode="Markdown")
    msgs = get_messages(user['token'])
    if not msgs:
        bot.send_message(message.chat.id, "📭 ইনবক্স এখনো খালি।")
    else:
        for m in msgs[:3]:
            sender = m['from']['address']
            subject = m['subject'] or "No Subject"
            bot.send_message(message.chat.id, f"📩 *From:* {sender}\n📝 *Subject:* {subject}", parse_mode="Markdown")

# --- কলব্যাক হ্যান্ডলার ---

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "gen_mail":
        bot.answer_callback_query(call.id, "Generating...")
        process_gen_mail(call.message.chat.id)
        
    elif call.data == "refresh_inbox":
        user = user_data.get(call.message.chat.id)
        if not user:
            bot.answer_callback_query(call.id, "Session Expired!")
            return
        
        bot.answer_callback_query(call.id, "Checking...")
        msgs = get_messages(user['token'])
        if not msgs:
            bot.send_message(call.message.chat.id, "📭 ইনবক্স এখনো খালি।")
        else:
            for m in msgs[:3]:
                sender = m['from']['address']
                subject = m['subject'] or "No Subject"
                bot.send_message(call.message.chat.id, f"📩 *New Mail!*\nFrom: {sender}\nSubject: {subject}", parse_mode="Markdown")

# --- ওয়েব সার্ভার ---
@app.route('/')
def index():
    return render_template('index.html')

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

if __name__ == "__main__":
    t = Thread(target=run_flask)
    t.start()
    print(f"Bot started successfully by @{ADMIN_ID}")
    bot.infinity_polling()
