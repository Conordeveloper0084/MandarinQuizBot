import os
from dotenv import load_dotenv

# .env faylni yuklash
load_dotenv()

# Muahit o‘zgaruvchilarini o‘qish
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN topilmadi! .env faylda yoki Render sozlamalarida BOT_TOKEN ni tekshiring.")

CHANNEL_ID = os.getenv("CHANNEL_ID", "@Conordevs_Blogs")

ADMINS = [int(admin_id) for admin_id in os.getenv("ADMINS", "").split(",") if admin_id]
if not ADMINS:
    print("Ogohlantirish: ADMINS ro‘yxati bo‘sh. Admin ID’larini tekshiring.")