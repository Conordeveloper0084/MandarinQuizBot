# Botni ishga tushuruvchi asosiy file!
from dotenv import load_dotenv
import os
from aiogram import executor
from loader import dp
import handlers

load_dotenv()

if __name__ == "__main__":
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN topilmadi! .env faylda yoki muhit o‘zgaruvchilarida tekshiring.")
    print("BOT_TOKEN is:", BOT_TOKEN)  # Faqat mahalliy sinov uchun
    executor.start_polling(dp, skip_updates=True)