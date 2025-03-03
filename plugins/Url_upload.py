import os
import re
from pyrogram import Client, filters
from pyrogram.types import Message
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

    # Ask the user for the desired quality
    await message.reply_text("Please choose the video quality (240, 360, 480, 720):")

    # Store the link, caption, and chat ID in user_data
    user_data[message.from_user.id] = {
        "link": madxapi_link,
        "caption": caption,
        "chat_id": message.chat.id
    }

# Handle quality input
@Client.on_message(filters.text & ~filters.command("yl"))
async def handle_quality(client: Client, message: Message):
    user_id = message.from_user.id

    # Check if the user is in the middle of a download process
    if user_id not in user_data:
        return

    # Validate the quality input
    quality = message.text.strip()
    if quality not in ["240", "360", "480", "720"]:
        await message.reply_text("Invalid quality. Please choose from 240, 360, 480, or 720.")
        return

    # Get the madxapi link, caption, and chat ID
    madxapi_link = user_data[user_id]["link"]
    caption = user_data[user_id]["caption"]
    chat_id = user_data[user_id]["chat_id"]

    # Start downloading the video
    await message.reply_text(f"Downloading video in {quality}p...")

    # Configure yt-dlp options
    output_template = f"downloads/{user_id}_video.mp4"
    ydl_opts = {
        "format": f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]",
        "outtmpl": output_template,
        "progress_hooks": [lambda d: progress_hook(d, client, chat_id)],
    }

    try:
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
        del user_data[user_id]
    except Exception as e:
        await message.reply_text(f"Failed to download video: {e}")

# Progress hook to show download progress
def progress_hook(d, client, chat_id):
    if d["status"] == "downloading":
        progress = d["_percent_str"]
        speed = d["_speed_str"]
        eta = d["_eta_str"]
        client.send_message(chat_id, f"Downloading... {progress} at {speed}, ETA: {eta}")


