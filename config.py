import re, os
from os import environ

id_pattern = re.compile(r'^.\d+$') 

API_ID = os.environ.get("API_ID", "22012880")
API_HASH = os.environ.get("API_HASH", "5b0e07f5a96d48b704eb9850d274fe1d")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "") 

FORCE_SUB = os.environ.get("FORCE_SUB", "") 

DB_NAME = os.environ.get("DB_NAME","Z900")     
DB_URL = os.environ.get("DB_URL","")

START_PIC = os.environ.get("START_PIC", "https://graph.org/file/ad48ac09b1e6f30d2dae4.jpg")
ADMIN = [int(admin) if id_pattern.search(admin) else admin for admin in os.environ.get('ADMIN', '6803505727').split()]
PORT = os.environ.get("PORT", "8080")

ERROR_MESSAGE = bool(os.environ.get('ERROR_MESSAGE', True))
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1002027394591"))
NEW_REQ_MODE = bool(environ.get('NEW_REQ_MODE', False))
SESSION_STRING = os.environ.get("SESSION_STRING", "")
REACTIONS = ["🤝", "😇", "🤗", "😍", "🎅", "🥰", "🤩", "😘", "😛", "😈", "🎉", "🫡", "😎", "🔥", "🤭", "🌚", "🆒", "👻", "😁"] #don't add any emoji because tg not support all emoji reactions
