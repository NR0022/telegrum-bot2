import json
import time
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler
)

# 🔐 VALID Telegram Bot Token দিন নিচের লাইনে
TOKEN = "7535909785:AAE7r25s5gzt3GEUWGYf49PcJgi6dNzAD-c"

# States
LOGIN, MAIN_MENU = range(2)

# Files
KEY_FILE = "keys.json"
USER_FILE = "user_data.json"

# Keyboard layouts
def login_keyboard():
    return ReplyKeyboardMarkup([["🔐 লগইন"]], resize_keyboard=True)

def user_menu_keyboard():
    return ReplyKeyboardMarkup(
        [["📄 মেনু অপশন ১"], ["📄 মেনু অপশন ২"], ["🚪 লগআউট"]],
        resize_keyboard=True
    )

# Utility functions
def load_keys():
    try:
        with open(KEY_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def load_users():
    try:
        with open(USER_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

def is_key_valid(key):
    keys = load_keys()
    return key in keys and time.time() < keys[key]

def is_logged_in(user_id):
    users = load_users()
    if str(user_id) in users:
        key = users[str(user_id)]['key']
        if is_key_valid(key):
            return True
    return False

def logout_user(user_id):
    users = load_users()
    if str(user_id) in users:
        del users[str(user_id)]
        save_users(users)

# Bot Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if is_logged_in(user_id):
        await update.message.reply_text("✅ আপনি লগইন আছেন।", reply_markup=user_menu_keyboard())
        return MAIN_MENU
    else:
        logout_user(user_id)
        await update.message.reply_text("🔑 Key দিন: (Admin থেকে পাওয়া Key)", reply_markup=ReplyKeyboardRemove())
        return LOGIN

async def handle_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    key = update.message.text.strip()

    if is_key_valid(key):
        users = load_users()
        users[str(user_id)] = {'key': key}
        save_users(users)
        await update.message.reply_text("✅ সফলভাবে লগইন হয়েছে!", reply_markup=user_menu_keyboard())
        return MAIN_MENU
    else:
        await update.message.reply_text("❌ Key সঠিক নয় বা মেয়াদ শেষ হয়েছে। আবার চেষ্টা করুন।")
        return LOGIN

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not is_logged_in(user_id):
        await update.message.reply_text(
            "❌ আপনার Key এর মেয়াদ শেষ হয়েছে। Admin থেকে নতুন Key নিয়ে পুনরায় লগইন করুন।",
            reply_markup=login_keyboard()
        )
        return LOGIN

    text = update.message.text

    if text == "📄 মেনু অপশন ১":
        await update.message.reply_text("📄 আপনি মেনু অপশন ১ নির্বাচন করেছেন।")
    elif text == "📄 মেনু অপশন ২":
        await update.message.reply_text("📄 আপনি মেনু অপশন ২ নির্বাচন করেছেন।")
    elif text == "🚪 লগআউট":
        logout_user(user_id)
        await update.message.reply_text("👋 আপনি লগআউট হয়েছেন।", reply_markup=login_keyboard())
        return LOGIN
    else:
        await update.message.reply_text("❓ বুঝতে পারিনি।")

    return MAIN_MENU

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LOGIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_key)],
            MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler)],
        },
        fallbacks=[],
    )

    app.add_handler(conv_handler)
    print("✅ User Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
