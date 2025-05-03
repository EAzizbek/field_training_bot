import os
from dotenv import load_dotenv

# .env faylni yuklaymiz
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL")  # Django backend API manzili
ADMIN_ID = os.getenv("ADMIN_ID")

# Debug uchun tekshirish
if not BOT_TOKEN:
    print("BOT_TOKEN .env faylda yo‘q!")
if not BACKEND_URL:
    print("BACKEND_URL .env faylda yo‘q!")
if not ADMIN_ID:
    print("ADMIN_ID .env faylda yoq!")
