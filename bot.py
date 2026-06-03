from telegram.ext import Application, CommandHandler, CallbackQueryHandler
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