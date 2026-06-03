"""
اسکریپت اصلاح خودکار تمام خطاهای PEP8
اجرا: python fix_pep8.py
"""

import os
import shutil

# ============================================
# محتوای اصلاح شده همه فایل‌ها
# ============================================

FILES = {
    "bot.py": '''from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from config import BOT_TOKEN
from database.models import create_tables
from handlers.start import start
from handlers.quiz import start_quiz, handle_answer
from handlers.profile import profile
import os


def main():
    # ساخت پوشه data اگر وجود نداره
    os.makedirs("data", exist_ok=True)

    # ساخت جداول دیتابیس
    create_tables()
    print("✅ دیتابیس ساخته شد")

    # ساخت اپلیکیشن
    app = Application.builder().token(BOT_TOKEN).build()

    # اضافه کردن هندلرها
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("quiz", start_quiz))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(CallbackQueryHandler(handle_answer, pattern="^ans_"))

    print("🤖 ربات اجرا شد...")
    app.run_polling()


if __name__ == "__main__":
    main()
''',

    "config.py": '''import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
''',

    "database/__init__.py": "",

    "database/models.py": '''import sqlite3


def create_tables(db_path="data/persona_bot.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            mbti_type TEXT NOT NULL,
            ei_score INTEGER NOT NULL,
            sn_score INTEGER NOT NULL,
            tf_score INTEGER NOT NULL,
            jp_score INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    """)

    conn.commit()
    conn.close()
''',

    "database/db.py": '''import sqlite3

DB_PATH = "data/persona_bot.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def add_user(user_id, username, first_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id, username, first_name) "
        "VALUES (?, ?, ?)",
        (user_id, username, first_name)
    )
    conn.commit()
    conn.close()


def user_exists(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None


def save_result(user_id, mbti_type, ei, sn, tf, jp):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO test_results "
        "(user_id, mbti_type, ei_score, sn_score, tf_score, jp_score) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, mbti_type, ei, sn, tf, jp)
    )
    conn.commit()
    conn.close()


def get_latest_result(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT mbti_type, ei_score, sn_score, tf_score, jp_score "
        "FROM test_results WHERE user_id = ? "
        "ORDER BY created_at DESC LIMIT 1",
        (user_id,)
    )
    result = cursor.fetchone()
    conn.close()
    return result
''',

    "handlers/__init__.py": "",

    "handlers/start.py": '''from telegram import Update
from telegram.ext import ContextTypes
from database.db import add_user, user_exists


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if not user_exists(user.id):
        add_user(user.id, user.username, user.first_name)

    welcome_text = f"""
👋 سلام {user.first_name} عزیز!

به ربات PersonaLink خوش اومدی! 🧠✨

من می‌تونم تیپ شخصیتی MBTI تو رو تشخیص بدم.

📝 با دستور /quiz تست رو شروع کن
📊 با دستور /profile نتیجه‌ات رو ببین

آماده‌ای خودت رو بهتر بشناسی؟ 🚀
    """

    await update.message.reply_text(welcome_text)
''',

    "handlers/profile.py": '''from telegram import Update
from telegram.ext import ContextTypes
from database.db import get_latest_result


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    result = get_latest_result(user.id)

    if not result:
        await update.message.reply_text("❌ هنوز هیچ تستی ندادی!\\nبا /quiz شروع کن.")
        return

    mbti_type, ei, sn, tf, jp = result

    def axis_text(score, positive, negative):
        return f"{positive} {score}٪ | {negative} {100-score}٪"

    profile_text = f"""
🧠 **پروفایل شخصیتی {user.first_name}**

✨ تیپ شخصیتی: **{mbti_type}**

📊 درصد محورها:

• {axis_text(ei, 'برون‌گرایی (E)', 'درون‌گرایی (I)')}
• {axis_text(sn, 'حسی (S)', 'شهودی (N)')}
• {axis_text(tf, 'منطقی (T)', 'احساسی (F)')}
• {axis_text(jp, 'ساختارگرا (J)', 'منعطف (P)')}

🔍 با دستور /quiz می‌تونی دوباره تست بدی.
    """

    await update.message.reply_text(profile_text, parse_mode="Markdown")
''',

    "handlers/quiz.py": '''import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db import save_result
from services.mbti_calculator import calculate_mbti

# لود کردن سوالات
with open("data/questions.json", "r", encoding="utf-8") as f:
    QUESTIONS = json.load(f)


async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع تست: ریست کردن داده‌های جلسه کاربر"""
    context.user_data["quiz"] = {
        "current_q": 0,
        "scores": {"EI": 0, "SN": 0, "TF": 0, "JP": 0}
    }
    await send_question(update, context)


async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ارسال سوال فعلی با دکمه‌ها"""
    quiz = context.user_data["quiz"]
    q_index = quiz["current_q"]

    if q_index >= len(QUESTIONS):
        await finish_quiz(update, context)
        return

    q = QUESTIONS[q_index]
    keyboard = []

    for option_text, score in q["options"]:
        keyboard.append([
            InlineKeyboardButton(
                option_text,
                callback_data=f"ans_{q_index}_{score}"
            )
        ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"❓ سوال {q_index + 1} از {len(QUESTIONS)}:\\n\\n{q['text']}",
        reply_markup=reply_markup
    )


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش جواب کاربر"""
    query = update.callback_query
    await query.answer()

    # استخراج اندیس سوال و امتیاز از callback_data
    data = query.data.split("_")  # ans_0_2
    q_index = int(data[1])
    score = int(data[2])

    quiz = context.user_data["quiz"]

    # بررسی معتبر بودن جواب
    if q_index != quiz["current_q"]:
        await query.message.edit_text("⚠️ این سوال قبلاً جواب داده شده.")
        return

    # ذخیره امتیاز
    axis = QUESTIONS[q_index]["axis"]
    quiz["scores"][axis] += score

    # حذف پیام قبلی
    await query.message.delete()

    # رفتن به سوال بعدی
    quiz["current_q"] += 1
    await send_question(query.message, context)


async def finish_quiz(update_or_query, context: ContextTypes.DEFAULT_TYPE):
    """پایان تست و محاسبه نتیجه"""
    quiz = context.user_data["quiz"]
    scores = quiz["scores"]

    mbti = calculate_mbti(scores)

    # ذخیره در دیتابیس
    user = update_or_query.effective_user
    save_result(user.id, mbti, scores["EI"],
                scores["SN"], scores["TF"], scores["JP"])

    # نمایش نتیجه
    result_text = f"""
🎉 **تست تموم شد!**

✨ تیپ شخصیتی تو: **{mbti}**

📊 امتیازات خام:
• E/I: {scores['EI']}
• S/N: {scores['SN']}
• T/F: {scores['TF']}
• J/P: {scores['JP']}

📋 برای دیدن پروفایل کامل: /profile
    """

    await update_or_query.message.reply_text(
        result_text,
        parse_mode="Markdown"
    )
''',

    "services/__init__.py": "",

    "services/mbti_calculator.py": '''def calculate_mbti(scores):
    """
    scores = {"EI": 3, "SN": -1, "TF": 5, "JP": -2}
    برمیگردونه: "ENTJ"
    """
    mbti = ""
    mbti += "E" if scores.get("EI", 0) > 0 else "I"
    mbti += "S" if scores.get("SN", 0) > 0 else "N"
    mbti += "T" if scores.get("TF", 0) > 0 else "F"
    mbti += "J" if scores.get("JP", 0) > 0 else "P"
    return mbti
''',

    "utils/__init__.py": "",

    "utils/helpers.py": "",
}


def fix_all_files():
    """بازنویسی همه فایل‌ها با محتوای اصلاح شده"""
    print("🔧 شروع اصلاح فایل‌ها...")
    
    for filepath, content in FILES.items():
        # ساخت پوشه اگر وجود نداره
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # نوشتن فایل
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"  ✅ {filepath}")
    
    print("\\n🎉 همه فایل‌ها با موفقیت اصلاح شدن!")
    print("📦 آماده برای commit و push")


if __name__ == "__main__":
    fix_all_files()
