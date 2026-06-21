import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

user_data = {}

def now():
    return datetime.now()

def get_user(user):
    return f"{user.first_name} ({user.id})"


# ---------------- START MENU ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🟢 Start Work", callback_data="start")],
        [InlineKeyboardButton("☕ Break", callback_data="break")],
        [InlineKeyboardButton("🪑 Back to Seat", callback_data="back")],
        [InlineKeyboardButton("🔴 Off Work", callback_data="off")]
    ]

    await update.message.reply_text(
        "📊 Office Time Management Bot\nChoose action:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ---------------- CORE LOGIC ----------------
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    user = q.from_user
    uid = user.id
    name = get_user(user)
    action = q.data

    if uid not in user_data:
        user_data[uid] = {
            "last_time": now(),
            "log": [],
            "total": 0
        }

    last = user_data[uid]["last_time"]
    current = now()
    minutes = (current - last).total_seconds() / 60

    msg = ""

    if action == "start":
        msg = f"🟢 {name} started work"

    elif action == "break":
        msg = f"☕ {name} break time: {minutes:.1f} min"

    elif action == "back":
        msg = f"🪑 {name} back to seat after {minutes:.1f} min"

    elif action == "off":
        msg = f"🔴 {name} off work. Session: {minutes:.1f} min"

    user_data[uid]["last_time"] = current
    user_data[uid]["log"].append(msg)
    user_data[uid]["total"] += minutes

    await q.edit_message_text(msg)


# ---------------- REPORT ----------------
async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    if uid not in user_data:
        await update.message.reply_text("No data found")
        return

    data = user_data[uid]
    text = "📊 Your Report:\n\n"

    for l in data["log"][-10:]:
        text += l + "\n"

    text += f"\n⏱ Total Time: {data['total']:.1f} min"

    await update.message.reply_text(text)


# ---------------- RUN BOT ----------------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("report", report))
app.add_handler(CallbackQueryHandler(handle))

print("Bot running...")
app.run_polling()
