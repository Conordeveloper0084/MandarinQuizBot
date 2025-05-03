# app.py — Renderda asosiy ishga tushuruvchi fayl (polling orqali)
import logging
from aiogram import executor
from loader import dp
import handlers  # Barcha handlerlaring shu papkada bo‘lishi kerak

# Logging
logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)