from plugins.Rename.utils import progress_for_pyrogram, convert, humanbytes
from pyrogram import Client, filters
from plugins.Rename.filedetect import refunc
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from helper.database import db
import os
import humanize
from PIL import Image
import time
import logging
from config import LOG_CHANNEL

logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

@Client.on_callback_query(filters.regex('cancel'))
async def cancel(bot, update):
    try:
        await update.message.delete()
    except Exception as e:
        logger.error(f"Cancel Error: {e}")
        return

@Client.on_callback_query(filters.regex("upload"))
async def doc(bot, update):
    try:
        type = update.data.split("_")[1]
        new_name = update.message.text
        new_filename = new_name.split(":-")[1].strip()
        file = update.message.reply_to_message
        file_path = f"downloads/{new_filename}"
        ms = await update.message.edit("⚠️ __Downloading file to my server...__")
        c_time = time.time()

        try:
            path = await bot.download_media(
                message=file,
                progress=progress_for_pyrogram,
                progress_args=("**⚠️ Please wait processing**", ms, c_time))
        except Exception as e:
            await ms.edit(f"❌ Download Error: {e}")
            return

        os.rename(path, file_path)
        logger.info(f"File downloaded and renamed to {file_path}")

        # Extract metadata
        duration = 0
        try:
            metadata = extractMetadata(createParser(file_path))
            if metadata and metadata.has("duration"):
                duration = metadata.get('duration').seconds
        except Exception as e:
            logger.error(f"Metadata Error: {e}")

        user = update.from_user
        c_caption = await db.get_caption(user.id)
        c_thumb = await db.get_thumbnail(user.id)

        # Extract file size safely
        try:
            media = getattr(file, file.media.value, None)
            filesize = humanize.naturalsize(media.file_size) if media and media.file_size else "Unknown Size"
        except AttributeError:
            filesize = "Unknown Size"

        # Prepare caption
        if c_caption:
            try:
                caption = c_caption.format(filename=new_filename, filesize=filesize, duration=convert(duration))
            except Exception as e:
                await ms.edit(f"❌ Caption Error: {e}")
                return
        else:
            caption = f"📂 **{new_filename}**"

        # Download and process thumbnail
        ph_path = None
        try:
            if c_thumb:
                ph_path = await bot.download_media(c_thumb)
            elif media and hasattr(media, "thumbs") and media.thumbs:
                ph_path = await bot.download_media(media.thumbs[0].file_id)

            if ph_path:
                Image.open(ph_path).convert("RGB").save(ph_path)
                img = Image.open(ph_path)
                img.resize((320, 320))
                img.save(ph_path, "JPEG")
        except Exception as e:
            logger.error(f"Thumbnail Error: {e}")
            ph_path = None

        await ms.edit("⚠️ __Processing file upload...__")
        c_time = time.time()

        # Send function mapping
        send_func = {
            "document": bot.send_document,
            "video": bot.send_video,
            "audio": bot.send_audio
        }.get(type, None)

        if send_func is None:
            await ms.edit("❌ Unknown file type. Cannot upload.")
            return

        # Prepare upload parameters
        upload_params = {
            "chat_id": user.id,
            type: file_path,
            "caption": caption,
        }
        if type in ["video", "audio"]:
            upload_params["thumb"] = ph_path
            upload_params["duration"] = duration

        # Send file to user
        try:
            await send_func(**upload_params, progress=progress_for_pyrogram, progress_args=("⚠️ Uploading file...", ms, c_time))
            logger.info(f"File {new_filename} sent to user {user.id}")
        except Exception as e:
            await ms.edit(f"❌ Upload Error: {e}")
            return

        # Send log to LOG_CHANNEL
        log_caption = (
            f"📩 **New File Saved** ☝🏻☝🏻\n\n"
            f"**☃️ Nᴀᴍᴇ:** {user.mention}\n"
            f"👤 **User ID:** `{user.id}`\n"
            f"📄 **Filename:** `{new_filename}`\n"
            f"📦 **Size:** {filesize}"
        )
        upload_params["chat_id"] = LOG_CHANNEL
        upload_params["caption"] = log_caption

        try:
            await send_func(**upload_params)
            logger.info(f"File {new_filename} logged in LOG_CHANNEL")
        except Exception as e:
            logger.error(f"Log Channel Upload Error: {e}")

        # Cleanup
        await ms.delete()
        os.remove(file_path)
        if ph_path:
            os.remove(ph_path)

    except Exception as e:
        logger.error(f"Unexpected Error: {e}")

	    
