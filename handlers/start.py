from telegram import Update
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