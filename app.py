# app.py - Telegram botni ishga tushuruvchi fayl (polling asosida, Render uchun)

import logging
import os
from aiogram import executor
from loader import dp  # bot ham u yerda
import handlers
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)