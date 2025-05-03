import os
import threading
from flask import Flask
from aiogram import executor
from loader import dp  

# Flask ilovasi
app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, World!"

def start_flask():
    """Flask ilovasini ishga tushirish"""
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

def start_bot():
    """Aiogram botini ishga tushirish"""
    executor.start_polling(dp, skip_updates=True)

if __name__ == "__main__":
    # Flask va botni alohida thread-larda ishga tushirish
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.start()

    start_bot()