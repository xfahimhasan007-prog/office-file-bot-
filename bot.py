import os
import sqlite3
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

conn = sqlite3.connect("office.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS logs (
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
name TEXT,
action TEXT,
minutes REAL,
time TEXT
)
""")
conn.commit()

user_state = {}

def now():
    return datetime.now()

def get_name(user):
    return f"{user.first_name} ({user.id})"

def save(uid, name, action, minutes):
    cursor.execute(
        "INSERT INTO logs (user_id, name, action, minutes, time) VALUES (?, ?, ?, ?, ?)",
        (uid, name, action, minutes, str(now()))
    )
    conn.commit()

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🟢 Start Work", callback_data="start")],
        [InlineKeyboardButton("☕ Break", callback_data="break")],
        [InlineKeyboardButton("🪑 Back", callback_data="back")],
        [InlineKeyboardButton("🔴 Off", callback_data="off")]
    ]

    await update.message.reply_text("👑 Office System Ready", reply_markup=InlineKeyboardMarkup(keyboard))

# ---------------- ACTION ----------------
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    user = q.from_user
    uid = user.id
    name = get_name(user)
    action = q.data

    if uid not in user_state:
        user_state[uid] = {"last": now()}

    last = user_state[uid]["last"]
    current = now()
    minutes = (current - last).total_seconds() / 60

    msg = f"{name} -> {action} ({minutes:.1f} min)"

    user_state[uid]["last"] = current
    save(uid, name, action, minutes)

    await q.edit_message_text(msg)

# ---------------- RUN BOT ----------------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle))

print("Bot running...")
app.run_polling()
