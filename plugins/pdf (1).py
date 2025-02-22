import requests
import os
import re
import logging
import tempfile
from PIL import Image
from pyrogram import Client, filters
from PyPDF2 import PdfMerger
from pyrogram.types import Message
from config import LOG_CHANNEL

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
user_merge_state = {}  # Track if a user is in the merge process
user_file_metadata = {}  # Store metadata for each user's files
pending_filename_requests = {}  # Track pending filename requests

@Client.on_message(filters.command(["merge"]))
async def start_file_collection(client: Client, message: Message):
    user_id = message.from_user.id
    user_merge_state[user_id] = True  # Set user in merge state
    user_file_metadata[user_id] = []  # Reset file list for the user
    await message.reply_text(
        "**📤 Uᴘʟᴏᴀᴅ ʏᴏᴜʀ ғɪʟᴇs ɪɴ sᴇǫᴜᴇɴᴄᴇ, ᴛʏᴘᴇ /done ✅, ᴀɴᴅ ɢᴇᴛ ʏᴏᴜʀ ᴍᴇʀɢᴇᴅ PDF !! 🧾**"
    )

@Client.on_message(filters.document & filters.private)
async def handle_pdf_metadata(client: Client, message: Message):
    user_id = message.from_user.id

    # Only process PDFs if the user is in the merge state
    if user_id not in user_merge_state or not user_merge_state[user_id]:
        return

    if message.document.mime_type != "application/pdf":
        await message.reply_text("❌ This is not a valid PDF file. Please send a PDF 📑.")
        return

    if len(user_file_metadata[user_id]) >= 20:
        await message.reply_text("⚠️ You can upload up to 20 files. Type /done ✅ to merge them.")
        return

    if message.document.file_size > MAX_FILE_SIZE:
        await message.reply_text("🚫 File size is too large! Please send a file under 20MB.")
        return

    user_file_metadata[user_id].append(
        {
            "type": "pdf",
            "file_id": message.document.file_id,
            "file_name": message.document.file_name,
        }
    )
    await message.reply_text(
        f"**➕ PDF ᴀᴅᴅᴇᴅ ᴛᴏ ᴛʜᴇ ʟɪsᴛ! 📄 ({len(user_file_metadata[user_id])} files added so far.)**\n"
        "**Sᴇɴᴅ ᴍᴏʀᴇ ғɪʟᴇs ᴏʀ ᴜsᴇ /done ✅ ᴛᴏ ᴍᴇʀɢᴇ ᴛʜᴇᴍ.**"
    )

@Client.on_message(filters.photo & filters.private)
async def handle_image_metadata(client: Client, message: Message):
    user_id = message.from_user.id

    # Only process images if the user is in the merge state
    if user_id not in user_merge_state or not user_merge_state[user_id]:
        return

    user_file_metadata[user_id].append(
        {
            "type": "image",
            "file_id": message.photo.file_id,
            "file_name": f"photo_{len(user_file_metadata[user_id]) + 1}.jpg",
        }
    )
    await message.reply_text(
        f"➕ Image added to the list! 🖼️ ({len(user_file_metadata[user_id])} files added so far.)\n"
        "Send more files or use /done ✅ to merge them."
    )

