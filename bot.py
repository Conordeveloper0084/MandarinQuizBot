# Botni ishga tushuruvchi asosiy file!
from dotenv import load_dotenv
import os
from aiogram import executor
from loader import dp
import handlers

load_dotenv()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

BOT_TOKEN = os.getenv("BOT_TOKEN")  

print("BOT_TOKEN is:", BOT_TOKEN)