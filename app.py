import os
import requests
from flask import Flask, render_template
import telebot
from threading import Thread

# --- কনফিগারেশন ---
TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN' # এখানে আপনার টেলিগ্রাম বোট টোকেন দিন
app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)

API_BASE = "https://api.mail.tm"

# --- বোটের ফাংশনালিটি ---

def generate_email():
    try:
        # ডোমেইন লিস্ট আনা
        domain_res = requests.get(f"{API_BASE}/domains").json()
        domain = domain_res['hydra:member'][0]['domain']
        
        # ইউজার এবং পাসওয়ার্ড তৈরি
        import random
        import string
        user = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        address = f"{user}@{domain}"
        
        # অ্যাকাউন্ট তৈরি
        data = {"address": address, "password": password}
        requests.post(f"{API_BASE}/accounts", json=data)
        
        return address, password
    except Exception as e:
        return None, None

@bot.message_handler(commands=['start', 'new'])
def send_welcome(message):
    bot.reply_to(message, "🔄 Generating your Temp Mail...")
    email, password = generate_email()
    if email:
        msg = (f"📧 *Your Temp Email:* `{email}`\n"
               f"🔑 *Password:* `{password}`\n\n"
               f"ইউজ করুন এই ইমেইলটি। ইনবক্স চেক করতে বোটের সাথে থাকুন।")
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ Error generating email. Try again.")

# --- ফ্লাস্ক ওয়েব সার্ভার ---

@app.route('/')
def index():
    # এটি আপনার HTML ফাইলটি দেখাবে
    return render_template('index.html')

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

def run_bot():
    bot.polling(none_stop=True)

if __name__ == "__main__":
    # বোট এবং ওয়েব সার্ভার একসাথে চালানোর জন্য থ্রেডিং
    t = Thread(target=run_flask)
    t.start()
    run_bot()
