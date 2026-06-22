import json
import random
import sqlite3
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# 🔑 BOT TOKEN (FAQAT BIR MARTA)
TOKEN = "8892651733:AAE1Kvvemb_5Y_E_F18CRVaWxICpsZCC6Y0"

# 👑 CREATOR
CREATOR = "Shahriyor Isokulov"

# 💎 premium users
premium_users = set()

# 📊 DATABASE
conn = sqlite3.connect("quiz.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    score INTEGER DEFAULT 0
)
""")
conn.commit()

# 📂 WORDS LOAD
with open("words.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

current = {}

# 🔘 BUTTONS
keyboard = ReplyKeyboardMarkup(
    [["A", "B"], ["C", "D"], ["/menu", "/score", "/top"]],
    resize_keyboard=True
)

# ➕ USER ADD
def add_user(user):
    cur.execute(
        "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
        (user.id, user.username or "NoName")
    )
    conn.commit()

# 💎 CHECK PREMIUM
def is_premium(user_id):
    return user_id in premium_users

# 📘 SEND QUESTION
async def send_question(update):
    user_id = update.effective_user.id

    available = []
    for q in questions:
        if q.get("premium") and not is_premium(user_id):
            continue
        available.append(q)

    q = random.choice(available)
    current[user_id] = q

    text = "📘 " + q["q"] + "\n\n" + "\n".join(q["o"])
    await update.message.reply_text(text, reply_markup=keyboard)

# 🚀 START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user)

    await update.message.reply_text(
        "🎯 IELTS QUIZ BOT\n\n"
        f"👑 Creator: {CREATOR}\n"
        "📚 English Vocabulary Quiz\n\n"
        "👉 /menu bosing",
        reply_markup=keyboard
    )

    await send_question(update)

# 📌 MENU
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 MENU\n\n"
        f"👑 Creator: {CREATOR}\n\n"
        "/start - boshlash\n"
        "/score - ball\n"
        "/top - reyting\n"
        "/buy - premium"
    )

# 💬 ANSWER
async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text.upper()

    add_user(user)

    if user.id not in current:
        return await update.message.reply_text("Avval /start bosing")

    q = current[user.id]

    if text == q["a"]:
        cur.execute("UPDATE users SET score = score + 1 WHERE user_id=?", (user.id,))
        conn.commit()
        await update.message.reply_text("✅ To‘g‘ri!")
    else:
        await update.message.reply_text(f"❌ Xato! Javob: {q['a']}")

    await send_question(update)

# 🏆 SCORE
async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    row = cur.execute("SELECT score FROM users WHERE user_id=?", (user_id,)).fetchone()
    s = row[0] if row else 0

    await update.message.reply_text(f"🏆 Sizning ball: {s}")

# 🥇 TOP
async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rows = cur.execute("SELECT username, score FROM users ORDER BY score DESC LIMIT 10").fetchall()

    text = "🏆 TOP 10:\n\n"
    for i, r in enumerate(rows, 1):
        text += f"{i}. @{r[0]} — {r[1]} ball\n"

    await update.message.reply_text(text)

# 💎 BUY (FAKE PREMIUM)
async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    premium_users.add(user_id)

    await update.message.reply_text(
        "💎 Premium aktiv!\nEndi maxsus savollar ochildi!"
    )

# 🚀 APP START
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("menu", menu))
app.add_handler(CommandHandler("score", score))
app.add_handler(CommandHandler("top", top))
app.add_handler(CommandHandler("buy", buy))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer))

print("🚀 BOT ISHGA TAYYOR...")
app.run_polling()