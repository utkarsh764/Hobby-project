import re, os
from os import environ

id_pattern = re.compile(r'^.\d+$') 

API_ID = os.environ.get("API_ID", "22012880")
API_HASH = os.environ.get("API_HASH", "5b0e07f5a96d48b704eb9850d274fe1d")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "") 

FORCE_SUB = os.environ.get("FORCE_SUB", "") 

DB_NAME = os.environ.get("DB_NAME","Test2")     
DB_URL = os.environ.get("DB_URL","")

START_PIC = os.environ.get("START_PIC", "https://graph.org/file/ad48ac09b1e6f30d2dae4.jpg")
ADMIN = [int(admin) if id_pattern.search(admin) else admin for admin in os.environ.get('ADMIN', '6803505727').split()]
PORT = os.environ.get("PORT", "8080")

# Rename Info : If True Then Bot Rename File Else Not
RENAME_MODE = bool(environ.get('RENAME_MODE', True)) # Set True or False

ERROR_MESSAGE = bool(os.environ.get('ERROR_MESSAGE', False))
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1002027394591"))
NEW_REQ_MODE = bool(environ.get('NEW_REQ_MODE', False))
SESSION_STRING = os.environ.get("SESSION_STRING", "")
REACTIONS = ["🤝", "😇", "🤗", "😍", "🎅", "🥰", "🤩", "😘", "😛", "😈", "🎉", "🫡", "😎", "🔥", "🤭", "🌚", "🆒", "👻", "😁"] #don't add any emoji because tg not support all emoji reactions




#new
CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-1002027394591"))
FORCE_MSG = os.environ.get("FORCE_SUB_MESSAGE", "ʜᴇʟʟᴏ {first}\n\n<b>ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs ᴀɴᴅ ᴛʜᴇɴ ᴄʟɪᴄᴋ ᴏɴ ʀᴇʟᴏᴀᴅ button ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ʀᴇǫᴜᴇꜱᴛᴇᴅ ꜰɪʟᴇ.</b>")
F_SUB_1 = int(os.environ.get("F_SUB_1", "-1002481520987"))#put 0 to disable
F_SUB_2 = int(os.environ.get("F_SUB_2", "0"))#put 0 to disable
F_SUB_3 = int(os.environ.get("F_SUB_3", "0"))#put 0 to disable
F_SUB_4 = int(os.environ.get("F_SUB_4", "0"))#put 0 to disable

FORCE_PIC = os.environ.get("FORCE_PIC", "https://telegra.ph/file/e292b12890b8b4b9dcbd1.jpg")
