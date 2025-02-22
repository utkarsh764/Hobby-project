import os
import logging
import time
import asyncio
import pyrogram
import requests
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UsernameNotOccupied
from pyrogram.types import Message
from config import API_ID, API_HASH, BOT_TOKEN, SESSION_STRING, LOG_CHANNEL
import tempfile

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
start_time = time.time()
batch_temp = {"IS_BATCH": {}}

#————————————————————————————————————————————————————————————————————————————————————————————
# Progress Message Function
async def progress_message(current, total, message, type="Downloading"):
    """
    Display a progress message with speed, time left, and percentage.
    :param current: Bytes downloaded/uploaded so far.
    :param total: Total size of the file.
    :param message: The message object to edit.
    :param type: Type of operation (Downloading/Uploading).
    """
    try:
        # Calculate elapsed time
        elapsed_time = time.time() - start_time

        # Calculate percentage
        percent = current * 100 / total

        # Calculate speed in MB/s
        speed = current / elapsed_time / (1024 * 1024) if elapsed_time > 0 else 0

        # Calculate time left
        remaining_bytes = total - current
        time_left = remaining_bytes / (current / elapsed_time) if current > 0 else 0

        # Format time left
        hours, remainder = divmod(int(time_left), 3600)
        minutes, seconds = divmod(remainder, 60)
        time_left_str = f"{hours}h {minutes}m {seconds}s" if hours else f"{minutes}m {seconds}s"

        # Update progress message
        progress_text = (
            f"**{type}...**\n\n"
            f"📦 **Progress**: {percent:.1f}%\n"
            f"⚡ **Speed**: {speed:.2f} MB/s\n"
            f"⏳ **Time Left**: {time_left_str}\n"
            f"📄 **Processed**: {current / (1024 * 1024):.2f}MB / {total / (1024 * 1024):.2f}MB"
        )
        await message.edit_text(progress_text)
    except Exception as e:
        logger.error(f"Error in progress_message: {e}")

#————————————————————————————————————————————————————————————————————————————————————————————
# Cleanup Function
async def cleanup(message):
    """
    Clean up temporary files and status files.
    :param message: The message object associated with the process.
    """
    for file in [f'{message.id}downstatus.txt', f'{message.id}upstatus.txt']:
        if os.path.exists(file):
            os.remove(file)

#————————————————————————————————————————————————————————————————————————————————————————————
# Download Custom Thumbnail
async def download_custom_thumbnail(url):
    """
    Download a custom thumbnail from a URL.
    :param url: The URL of the thumbnail.
    :return: Path to the downloaded thumbnail file.
    """
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
                temp_file.write(response.content)
                return temp_file.name
        return None
    except Exception as e:
        logger.error(f"Error downloading custom thumbnail: {e}")
        return None

#————————————————————————————————————————————————————————————————————————————————————————————
# Cancel Command
@Client.on_message(filters.command("cancel") & filters.private)
async def cancel_command(client: Client, message: Message):
    """
    Cancel an ongoing batch download.
    """
    user_id = message.from_user.id
    if user_id in batch_temp["IS_BATCH"]:
        batch_temp["IS_BATCH"][user_id] = True
        await message.reply_text("✅ Batch download cancelled.")
    else:
        await message.reply_text("⚠️ No active batch download to cancel.")

#————————————————————————————————————————————————————————————————————————————————————————————
# Save Command
@Client.on_message(filters.text & filters.private & filters.regex("https://t.me/"))
async def save(client: Client, message: Message):
    if "https://t.me/" in message.text:
        if batch_temp["IS_BATCH"].get(message.from_user.id) == False:
            return await message.reply_text("**One Task Is Already Processing. Wait For It To Complete. If You Want To Cancel This Task Then Use - /cancel**")

        # Parse the message text for thumbnail URL
        parts = message.text.split("-t")
        file_link = parts[0].strip()
        thumbnail_url = parts[1].strip() if len(parts) > 1 else None

        datas = file_link.split("/")
        temp = datas[-1].replace("?single", "").split("-")
        fromID = int(temp[0].strip())
        try:
            toID = int(temp[1].strip())
        except:
            toID = fromID

        batch_temp["IS_BATCH"][message.from_user.id] = False

        # Connect using the session string
        acc = Client("manual_session", session_string=SESSION_STRING, api_hash=API_HASH, api_id=API_ID)
        await acc.connect()

        tasks = []
        for msgid in range(fromID, toID + 1):
            if batch_temp["IS_BATCH"].get(message.from_user.id):
                break

            # Handle private chats
            if "https://t.me/c/" in file_link:
                chatid = int("-100" + datas[4])
                tasks.append(handle_private(client, acc, message, chatid, msgid, thumbnail_url))

            # Handle public chats
            else:
                username = datas[3]
                tasks.append(handle_public(client, acc, message, username, msgid, thumbnail_url))

        await asyncio.gather(*tasks)
        batch_temp["IS_BATCH"][message.from_user.id] = True
        await acc.disconnect()

#————————————————————————————————————————————————————————————————————————————————————————————
# Handle Public Chats
async def handle_public(client: Client, acc, message: Message, username: str, msgid: int, thumbnail_url=None):
    try:
        msg = await client.get_messages(username, msgid)
    except UsernameNotOccupied:
        await client.send_message(message.chat.id, "The username is not occupied by anyone", reply_to_message_id=message.id)
        return

    try:
        await client.copy_message(message.chat.id, msg.chat.id, msg.id, reply_to_message_id=message.id)
        await client.copy_message(LOG_CHANNEL, msg.chat.id, msg.id)
    except Exception as e:
        logger.error(f"Error in handle_public: {e}")
        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

#————————————————————————————————————————————————————————————————————————————————————————————
# Handle Private Chats
async def handle_private(client: Client, acc, message: Message, chatid: int, msgid: int, thumbnail_url=None):
    msg: Message = await acc.get_messages(chatid, msgid)
    if msg.empty:
        return
    msg_type = get_message_type(msg)
    if not msg_type:
        return
    chat = message.chat.id
    user_id = message.from_user.id  # User's DM ID

    if batch_temp["IS_BATCH"].get(user_id):
        return

    if msg_type == "Text":
        try:
            text_msg = await client.send_message(user_id, msg.text, entities=msg.entities, parse_mode=enums.ParseMode.HTML)
            await client.send_message(LOG_CHANNEL, msg.text, entities=msg.entities, parse_mode=enums.ParseMode.HTML)
            return
        except Exception as e:
            logger.error(f"Error in handle_private (Text): {e}")
            await client.send_message(chat, f"Error: {e}", reply_to_message_id=message.id)
            return

    smsg = await client.send_message(chat, '**Downloading**', reply_to_message_id=message.id)

    try:
        file = await acc.download_media(msg, progress=progress_message, progress_args=[message, "Downloading"])
    except Exception as e:
        logger.error(f"Error in handle_private (Download): {e}")
        await client.send_message(chat, f"Error: {e}", reply_to_message_id=message.id)
        return await smsg.delete()

    if batch_temp["IS_BATCH"].get(user_id):
        return

    caption = msg.caption if msg.caption else None

    # Download custom thumbnail if provided
    custom_thumb = await download_custom_thumbnail(thumbnail_url) if thumbnail_url else None

    # Sending to both DM and log channel separately
    async def send_to_user_and_log(send_func, **kwargs):
        try:
            # Send to user's DM
            sent_msg = await send_func(user_id, **kwargs)

            # Send to log channel separately (new message)
            await send_func(LOG_CHANNEL, **kwargs)
        except Exception as e:
            logger.error(f"Error in send_to_user_and_log: {e}")
            await client.send_message(chat, f"Error: {e}", reply_to_message_id=message.id)

    if msg_type == "Document":
        thumb = custom_thumb or (await acc.download_media(msg.document.thumbs[0].file_id) if msg.document.thumbs else None)
        await send_to_user_and_log(client.send_document, document=file, thumb=thumb, caption=caption, parse_mode=enums.ParseMode.HTML)
        if thumb:
            os.remove(thumb)

    elif msg_type == "Video":
        thumb = custom_thumb or (await acc.download_media(msg.video.thumbs[0].file_id) if msg.video.thumbs else None)
        await send_to_user_and_log(client.send_video, video=file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=thumb, caption=caption, parse_mode=enums.ParseMode.HTML)
        if thumb:
            os.remove(thumb)

    elif msg_type == "Animation":
        await send_to_user_and_log(client.send_animation, animation=file, caption=caption, parse_mode=enums.ParseMode.HTML)

    elif msg_type == "Sticker":
        await send_to_user_and_log(client.send_sticker, sticker=file)

    elif msg_type == "Voice":
        await send_to_user_and_log(client.send_voice, voice=file, caption=caption, parse_mode=enums.ParseMode.HTML)

    elif msg_type == "Audio":
        thumb = custom_thumb or (await acc.download_media(msg.audio.thumbs[0].file_id) if msg.audio.thumbs else None)
        await send_to_user_and_log(client.send_audio, audio=file, thumb=thumb, caption=caption, parse_mode=enums.ParseMode.HTML)
        if thumb:
            os.remove(thumb)

    elif msg_type == "Photo":
        await send_to_user_and_log(client.send_photo, photo=file, caption=caption, parse_mode=enums.ParseMode.HTML)

    await cleanup(message)
    await smsg.delete()

#————————————————————————————————————————————————————————————————————————————————————————————
# Get Message Type
def get_message_type(msg: pyrogram.types.messages_and_media.message.Message):
    if msg.document:
        return "Document"
    elif msg.video:
        return "Video"
    elif msg.animation:
        return "Animation"
    elif msg.sticker:
        return "Sticker"
    elif msg.voice:
        return "Voice"
    elif msg.audio:
        return "Audio"
    elif msg.photo:
        return "Photo"
    elif msg.text:
        return "Text"
    return None


