from telegram import Update
from telegram.ext import ContextTypes
from database.db import get_latest_result

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    result = get_latest_result(user.id)
    
    if not result:
        await update.message.reply_text("❌ هنوز هیچ تستی ندادی!\nبا /quiz شروع کن.")
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