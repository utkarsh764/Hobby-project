import os
import re
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from yt_dlp import YoutubeDL

# Dictionary to store user states
user_data = {}

# Command to start the process
@Client.on_message(filters.command("yl"))
async def start_download(client: Client, message: Message):
    # Check if the user provided a madxapi link and caption
    if len(message.command) < 2 or "-n" not in message.text:
        await message.reply_text("Usage: /yl <madxapi_link> -n <caption>")
        return

    # Extract the madxapi link and caption
    text_parts = message.text.split("-n")
    madxapi_link = text_parts[0].split()[1].strip()
    caption = text_parts[1].strip()

    # Validate the madxapi link
    if not re.match(r"https://madxapi-d0cbf6ac738c\.herokuapp\.com/.*/master\.m3u8\?token=.*", madxapi_link):
        await message.reply_text("Invalid madxapi link. Please provide a valid link.")
        return

    # Store the link, caption, and chat ID in user_data
    user_data[message.from_user.id] = {
        "link": madxapi_link,
        "caption": caption,
        "chat_id": message.chat.id
    }

    # Create inline buttons for quality selection
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("240p", callback_data="quality_240"),
            InlineKeyboardButton("360p", callback_data="quality_360")],
            [InlineKeyboardButton("480p", callback_data="quality_480"),
            InlineKeyboardButton("720p", callback_data="quality_720")],
            [InlineKeyboardButton("✖️ Cancel ✖️", callback_data="cancel")]
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
        await callback_query.answer("Session expired. Please start again with /yl.")
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

        # Get the madxapi link, caption, and chat ID
        madxapi_link = user_data[user_id]["link"]
        caption = user_data[user_id]["caption"]
        chat_id = user_data[user_id]["chat_id"]

        # Start downloading the video
        await callback_query.message.edit_text(f"Downloading video in {quality}p...")

        # Configure yt-dlp options
        output_template = f"downloads/{user_id}_video.mp4"
        ydl_opts = {
            
            "format": f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]",
            "outtmpl": output_template,
            "progress_hooks": [lambda d: progress_hook(d, user_id, chat_id)],
            "external_downloader": "pycryptodomex"  # Use pycryptodomex for decryption
        }

        try:
            # Start a background task to monitor progress
            asyncio.create_task(monitor_progress(user_id, chat_id))

            # Download the video
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([madxapi_link])

            # Send the downloaded video to the user
            await client.send_video(
                chat_id=chat_id,
                video=output_template,
                caption=f"/yl {madxapi_link} -n {caption}"
            )

            # Clean up
            os.remove(output_template)
            del user_data[user_id]  # Clear user data after completion
        except Exception as e:
            await callback_query.message.reply_text(f"Failed to download video: {e}")
            del user_data[user_id]  # Clear user data on error

# Progress hook to update download progress
def progress_hook(d, user_id, chat_id):
    if d["status"] == "downloading":
        progress = d["_percent_str"]
        speed = d["_speed_str"]
        eta = d["_eta_str"]
        user_data[user_id]["progress"] = f"Downloading... {progress} at {speed}, ETA: {eta}"

# Background task to monitor progress and send updates
async def monitor_progress(user_id, chat_id):
    while user_id in user_data:
        if "progress" in user_data[user_id]:
            await app.send_message(chat_id, user_data[user_id]["progress"])
            await asyncio.sleep(3)  # Send progress updates every 3 seconds
        else:
            await asyncio.sleep(1)

