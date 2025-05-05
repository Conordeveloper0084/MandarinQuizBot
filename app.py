# app.py - Renderda asosiy ishga tushuruvchi file!
import os
import logging

from flask import Flask, request
from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_webhook
from loader import bot, dp
import handlers  
from dotenv import load_dotenv

load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)

# Webhook konfiguratsiyasi
WEBHOOK_HOST = 'https://mandarinquizbot-trt6.onrender.com'  
WEBHOOK_PATH = '/webhook'  # Ixtiyoriy, faqat oxirgi qismi
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

WEBAPP_HOST = "0.0.0.0"  # Flask uchun
WEBAPP_PORT = int(os.environ.get("PORT", 5000))  # Render beradi

# Flask ilova
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running!"

@app.route(WEBHOOK_PATH, methods=['POST'])
async def webhook():
    update = types.Update(**request.json)
    await dp.process_update(update)
    return "ok", 200

async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)
    print("Webhook set:", WEBHOOK_URL)

async def on_shutdown(dp):
    await bot.delete_webhook()
    print("Webhook deleted")

if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )