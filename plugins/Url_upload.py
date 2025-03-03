import os
import re
import asyncio
import logging
from yt_dlp import YoutubeDL
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

# Initialize logging
logger = logging.getLogger(__name__)

# Dictionary to store user states
user_data = {}

# Function to handle madxapi links
async def download_madxapi_link(client: Client, message: Message, url: str, quality: str):
    try:
        # Configure yt-dlp options for madxapi links
        output_template = f"downloads/{message.from_user.id}_video.mp4"
        ydl_opts = {
            "format": f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]",
            "outtmpl": output_template,
            "progress_hooks": [lambda d: progress_hook(d, client, message.chat.id)],
            "external_downloader": "ffmpeg",  # Use ffmpeg for decryption
            "verbose": True,  # Enable verbose logging
        }

        # Start downloading the video
        await message.reply_text(f"Downloading video in {quality}p...")

        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)  # Extract info first
            if not info_dict:
                await message.reply_text("Failed to extract video information. The URL might be invalid or unsupported.")
                return

            ydl.download([url])  # Download the video

        # Send the downloaded video to the user
        await client.send_video(
            chat_id=message.chat.id,
            video=output_template,
            caption=f"Downloaded from: {url}"
        )

        # Clean up
        os.remove(output_template)
    except Exception as e:
        logger.error(f"Failed to download video: {e}")
        await message.reply_text(f"Failed to download video: {e}")

# Progress hook to show download progress
def progress_hook(d, client, chat_id):
    if d["status"] == "downloading":
        progress = d["_percent_str"]
        speed = d["_speed_str"]
        eta = d["_eta_str"]
        asyncio.create_task(client.send_message(chat_id, f"Downloading... {progress} at {speed}, ETA: {eta}"))

# Command to start the process
@Client.on_message(filters.command("yl"))
async def start_madxapi_download(client: Client, message: Message):
    # Check if the user provided a madxapi link
    if len(message.command) < 2:
        await message.reply_text("Usage: /yl <link>")
        return

    # Extract the madxapi link
    madxapi_link = message.command[1]

    # Validate the madxapi link
    if not re.match(r"https://madxapi-d0cbf6ac738c\.herokuapp\.com/.*/master\.m3u8\?token=.*", madxapi_link):
        await message.reply_text("Invalid madxapi link. Please provide a valid link.")
        return

    # Store the link and chat ID in user_data
    user_data[message.from_user.id] = {
        "link": madxapi_link,
        "chat_id": message.chat.id
    }

    # Create inline buttons for quality selection
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("240p", callback_data="quality_240"),
            InlineKeyboardButton("360p", callback_data="quality_360")],
            [InlineKeyboardButton("480p", callback_data="quality_480"),
            InlineKeyboardButton("720p", callback_data="quality_720")],
            [InlineKeyboardButton("Cancel", callback_data="cancel")]
        ]
    )

    # Ask the user to select quality
    await message.reply_text("Please choose the video quality:", reply_markup=keyboard)

# Handle callback queries (quality selection)
@Client.on_callback_query()
async def handle_callback(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id

    # Check if the user is in the middle of a download process
    if user_id not in user_data:
        await callback_query.answer("Session expired. Please start again with /madxapi.")
        return

    # Get the callback data
    data = callback_query.data

    # Handle cancel button
    if data == "cancel":
        await callback_query.answer("Download cancelled.")
        del user_data[user_id]  # Clear user data
        await callback_query.message.delete()  # Delete the quality selection message
        return

    # Handle quality selection
    if data.startswith("quality_"):
        quality = data.split("_")[1]  # Extract quality (240, 360, 480, 720)
        await callback_query.answer(f"Downloading in {quality}p...")

        # Get the madxapi link and chat ID
        madxapi_link = user_data[user_id]["link"]
        chat_id = user_data[user_id]["chat_id"]

        # Start downloading the video
        await download_madxapi_link(client, callback_query.message, madxapi_link, quality)

        # Clear user data after completion
        del user_data[user_id]


