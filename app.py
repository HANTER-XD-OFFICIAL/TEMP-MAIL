import os
import requests
import random
import string
import telebot
from flask import Flask, render_template
from threading import Thread

# --- কনফিগারেশন ---
TOKEN = '8821453331:AAGG0KnJNrDT-nyKMAaa2xpa_lrp90nbK-I'
API_BASE = "https://api.mail.tm"

app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)

# ইউজার ডেটা স্টোর করার জন্য (সেশন অনুযায়ী)
user_data = {}

def generate_account():
    """mail.tm থেকে নতুন অ্যাকাউন্ট তৈরি করে"""
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
    """ইনবক্স চেক করে"""
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(f"{API_BASE}/messages", headers=headers).json()
    return res.get('hydra:member', [])

# --- টেলিগ্রাম বোট কমান্ডস ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "👋 *Temp Mail Pro তে স্বাগতম!*\n\n"
        "নিচের বাটনগুলো ব্যবহার করে ইমেইল তৈরি এবং চেক করুন।"
    )
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📧 Generate Email", "📥 Check Inbox")
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📧 Generate Email")
def make_email(message):
    bot.reply_to(message, "⏳ একটি নতুন ইমেইল তৈরি করা হচ্ছে...")
    email, password, token = generate_account()
    if email:
        user_data[message.chat.id] = {'email': email, 'token': token}
        response = (
            f"✅ *আপনার ইমেইল তৈরি হয়েছে:*\n\n"
            f"📧 *Address:* `{email}`\n"
            f"🔑 *Password:* `{password}`\n\n"
            f"এখন এই ইমেইলটি ব্যবহার করতে পারেন।"
        )
        bot.send_message(message.chat.id, response, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "❌ সমস্যা হয়েছে, আবার চেষ্টা করুন।")

@bot.message_handler(func=lambda message: message.text == "📥 Check Inbox")
def check_inbox(message):
    user = user_data.get(message.chat.id)
    if not user:
        bot.reply_to(message, "⚠️ আগে একটি ইমেইল তৈরি করুন (Generate Email এ ক্লিক করুন)।")
        return
    
    msgs = get_messages(user['token'])
    if not msgs:
        bot.send_message(message.chat.id, "📭 ইনবক্স খালি।")
    else:
        for m in msgs[:5]: # সর্বশেষ ৫টি মেসেজ দেখাবে
            sender = m['from']['address']
            subject = m['subject'] if m['subject'] else "(No Subject)"
            bot.send_message(message.chat.id, f"📩 *From:* {sender}\n📝 *Subject:* {subject}\n\nইনবক্সের বিস্তারিত আপনার ওয়েব লিংকে দেখুন।", parse_mode="Markdown")

# --- ফ্লাস্ক ওয়েব সার্ভার (আপনার HTML দেখানোর জন্য) ---

@app.route('/')
def index():
    # templates ফোল্ডারের ভেতরে আপনার index.html থাকতে হবে
    return render_template('index.html')

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

if __name__ == "__main__":
    # বোট এবং ফ্লাস্ক একসাথে চালানোর জন্য
    t = Thread(target=run_flask)
    t.start()
    print("Bot is starting...")
    bot.infinity_polling()
