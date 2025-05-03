import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils.executor import start_webhook
import os

API_TOKEN = os.getenv("BOT_TOKEN")

# Webhook settings:
WEBHOOK_HOST = 'https://mandarinquizbot.onrender.com'  # Render URL
WEBHOOK_PATH = f"/webhook/{API_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# Webserver settings:
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = int(os.getenv("PORT", default=10000))

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

async def on_startup(dispatcher):
    await bot.set_webhook(WEBHOOK_URL)
    print("Webhook set")

async def on_shutdown(dispatcher):
    await bot.delete_webhook()
    print("Webhook deleted")


if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )