import os
import threading
import logging
from flask import Flask
from aiogram import executor
from loader import dp
from dotenv import load_dotenv

load_dotenv()  # .env faylni yuklash

# Loglar
logging.basicConfig(level=logging.INFO)

# Flask ilovasi
app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, World! Bot is running."

def start_flask():
    """Flask ilovasini ishga tushirish"""
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

def start_bot():
    """Aiogram botini ishga tushirish"""
    executor.start_polling(dp, skip_updates=True)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()
    start_bot()