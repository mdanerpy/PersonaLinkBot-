import json
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
        keyboard.append([InlineKeyboardButton(option_text, callback_data=f"ans_{q_index}_{score}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"❓ سوال {q_index + 1} از {len(QUESTIONS)}:\n\n{q['text']}",
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
        await query.message.edit_text("⚠️ این سوال قبلاً جواب داده شده. ادامه بده...")
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
    save_result(user.id, mbti, scores["EI"], scores["SN"], scores["TF"], scores["JP"])
    
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
    
    await update_or_query.message.reply_text(result_text, parse_mode="Markdown")