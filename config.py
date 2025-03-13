import re, os
from os import environ

id_pattern = re.compile(r'^.\d+$') 

API_ID = os.environ.get("API_ID", "26926782")
API_HASH = os.environ.get("API_HASH", "9b2fac908fb7f9a3dabac3b0a57211b1")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "7786105206:AAHm0iceXktLQugF_5xs-lRj8xjbtMR-xE0") 

DB_NAME = os.environ.get("DB_NAME","Utkarsh9")     
DB_URL = os.environ.get("DB_URL","mongodb+srv://Utkarsh123:9335924360@utkarsh9.af91n.mongodb.net/?retryWrites=true&w=majority&appName=Utkarsh9")

ADMIN = [int(admin) if id_pattern.search(admin) else admin for admin in os.environ.get('ADMIN', '1214167849').split()]
PORT = os.environ.get("PORT", "8080")

RENAME_MODE = bool(environ.get('RENAME_MODE', True)) # Set True or False
ERROR_MESSAGE = bool(os.environ.get('ERROR_MESSAGE', False)) # Set True or False
NEW_REQ_MODE = bool(environ.get('NEW_REQ_MODE', False)) # Set True or False
SESSION_STRING = os.environ.get("SESSION_STRING", "")

START_PIC = os.environ.get("START_PIC", "https://graph.org/file/ad48ac09b1e6f30d2dae4.jpg")
FORCE_PIC = os.environ.get("FORCE_PIC", "https://telegra.ph/file/e292b12890b8b4b9dcbd1.jpg")
AUTH_CHANNEL = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('AUTH_CHANNEL', '-1002348383946').split()] #Ex : ('-10073828 -102782829 -1007282828')
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1002354465117"))

REACTIONS = ["🤝", "😇", "🤗", "😍", "🎅", "🥰", "🤩", "😘", "😛", "😈", "🎉", "🫡", "😎", "🔥", "🤭", "🌚", "🆒", "👻", "😁"] #don't add any emoji because tg not support all emoji reactions
