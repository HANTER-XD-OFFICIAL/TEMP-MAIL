import os
import requests
import random
import string
import telebot
from flask import Flask
from threading import Thread
from telebot import types

# --- Configuration ---
# Using the token you provided earlier
TOKEN = '8821453331:AAHA_14xkD-f_OjvCUlY5CQ5iVYxIENBPB4'
DEV_LINK = "https://t.me/HANTER_XD_OFFICIAL"
PORTFOLIO_LINK = "https://hanter-xd-official.github.io/PORTFOLIO/"
API_BASE = "https://api.mail.tm"

app = Flask(__name__)
bot = telebot.TeleBot(TOKEN)

# Session Storage
user_data = {}

# --- Mail.tm API Helper ---
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

# --- Email Generation Helper ---
def process_gen_mail(chat_id):
    email, password, token = generate_account()
    if email:
        user_data[chat_id] = {'email': email, 'token': token, 'pass': password}
        res_msg = (
            f"✨ *Your Temp Mail is Ready!*\n\n"
            f"📧 *Address:* `{email}`\n"
            f"🔑 *Password:* `{password}`\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 *Developer:* [HANTER_XD_OFFICIAL]({DEV_LINK})"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📥 Refresh Inbox", callback_data="refresh_inbox"))
        markup.add(types.InlineKeyboardButton("🔄 Generate New", callback_data="gen_mail"))
        bot.send_message(chat_id, res_msg, parse_mode="Markdown", reply_markup=markup, disable_web_page_preview=True)
    else:
        bot.send_message(chat_id, "❌ Error creating email. Please try again.")

# --- Start Handler ---

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        f"🌟 *Hi {message.from_user.first_name}! Welcome to Temp Mail Pro*\n\n"
        f"🔐 *Protect your privacy* by using a disposable email address for social media, "
        f"websites, and apps.\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 *Developer:* [HANTER_XD_OFFICIAL]({DEV_LINK})\n"
        f"🚀 *Status:* System Online ✅\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👇 *Use the buttons below to manage your mail:*"
    )
    
    inline_markup = types.InlineKeyboardMarkup(row_width=2)
    btn_gen = types.InlineKeyboardButton("📧 Generate Mail", callback_data="gen_mail")
    btn_web = types.InlineKeyboardButton("🌐 Visit Website", url=PORTFOLIO_LINK)
    btn_sup = types.InlineKeyboardButton("📢 Support", url=DEV_LINK)
    inline_markup.add(btn_gen)
    inline_markup.add(btn_web, btn_sup)

    reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    reply_markup.add("🗂️ LIVE GENERATE MAIL ⚡📢", "📥 Check Inbox")

    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=inline_markup, disable_web_page_preview=True)
    bot.send_message(message.chat.id, "💡 *Quick Access Menu Enabled*", parse_mode="Markdown", reply_markup=reply_markup)

@bot.message_handler(func=lambda m: m.text == "🗂️ LIVE GENERATE MAIL ⚡📢")
def handle_reply_gen(message):
    process_gen_mail(message.chat.id)

@bot.message_handler(func=lambda message: message.text == "📥 Check Inbox")
def handle_check_inbox_msg(message):
    user = user_data.get(message.chat.id)
    if not user:
        bot.reply_to(message, "⚠️ Please generate an email first!")
        return
    msgs = get_messages(user['token'])
    if not msgs:
        bot.send_message(message.chat.id, "📭 *Inbox is empty.*", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, "📥 *New messages found!*", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "gen_mail":
        bot.answer_callback_query(call.id, "Generating...")
        process_gen_mail(call.message.chat.id)
    elif call.data == "refresh_inbox":
        user = user_data.get(call.message.chat.id)
        if not user:
            bot.answer_callback_query(call.id, "Session Expired!", show_alert=True)
            return
        msgs = get_messages(user['token'])
        if not msgs:
            bot.answer_callback_query(call.id, "📭 Still Empty", show_alert=True)
        else:
            for m in msgs[:3]:
                headers = {"Authorization": f"Bearer {user['token']}"}
                m_detail = requests.get(f"{API_BASE}/messages/{m['id']}", headers=headers).json()
                bot.send_message(call.message.chat.id, f"📩 *From:* {m['from']['address']}\n📝 *Subject:* {m['subject']}\n\n{m_detail.get('text', '')[:500]}", parse_mode="Markdown")

# --- Web Server ---
@app.route('/')
def index():
    return "Bot is Live!"

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

if __name__ == "__main__":
    t = Thread(target=run_flask)
    t.start()
    bot.infinity_polling()
