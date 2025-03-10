
from plugins.Rename.utils import progress_for_pyrogram, convert, humanbytes
from pyrogram import Client, filters
from plugins.Rename.filedetect import refunc
from pyrogram.types import (  InlineKeyboardButton, InlineKeyboardMarkup,ForceReply)
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
async def cancel(bot,update):
    try:
        await update.message.delete()
    except:
        return

@Client.on_callback_query(filters.regex("upload"))
async def doc(bot, update):
    try:
        type = update.data.split("_")[1]
        new_name = update.message.text
        new_filename = new_name.split(":-")[1].strip()
        file = update.message.reply_to_message
        file_path = f"downloads/{new_filename}"
        ms = await update.message.edit("⚠️__**Please wait...**__\n__Downloading file to my server...__")
        c_time = time.time()
        
        try:
            path = await bot.download_media(
                message=file,
                progress=progress_for_pyrogram,
                progress_args=("**⚠️ Please wait processing**", ms, c_time))
        except Exception as e:
            await ms.edit(str(e))
            return
        
        os.rename(path, file_path)

        duration = 0
        try:
            metadata = extractMetadata(createParser(file_path))
            if metadata.has("duration"):
                duration = metadata.get('duration').seconds
        except:
            pass

        user = update.from_user
        c_caption = await db.get_caption(update.message.chat.id)
        c_thumb = await db.get_thumbnail(update.message.chat.id)

        if c_caption:
            try:
                caption = c_caption.format(filename=new_filename, filesize=humanize.naturalsize(file.file_size), duration=convert(duration))
            except Exception as e:
                await ms.edit(text=f"Your caption Error unexpected keyword ●> ({e})")
                return
        else:
            caption = f"**{new_filename}**"

        ph_path = None
        if file.thumbs or c_thumb:
            ph_path = await bot.download_media(c_thumb if c_thumb else file.thumbs[0].file_id)
            Image.open(ph_path).convert("RGB").save(ph_path)
            img = Image.open(ph_path)
            img.resize((320, 320))
            img.save(ph_path, "JPEG")

        await ms.edit("⚠️__**Please wait...**__\n\n__Processing file upload....__")
        c_time = time.time()

        send_func = {
            "document": bot.send_document,
            "video": bot.send_video,
            "audio": bot.send_audio
        }.get(type)

        if send_func:
            await send_func(
                update.message.chat.id,
                **{type: file_path},
                caption=caption,
                thumb=ph_path,
                duration=duration if type in ["video", "audio"] else None,
                progress=progress_for_pyrogram,
                progress_args=("⚠️__**Please wait...**__", ms, c_time)
            )

            # Send copy to log channel
            log_caption = (
                f"📩 **New File Saved** ☝🏻☝🏻\n\n"
                f"**☃️ Nᴀᴍᴇ:** {user.mention}\n"
                f"👤 **User ID:** `{user.id}`\n"
                f"📄 **Filename:** `{new_filename}`\n"
                f"📦 **Size:** {humanize.naturalsize(file.file_size)}"
            )
            await send_func(
                LOG_CHANNEL,
                **{type: file_path},
                caption=log_caption,
                thumb=ph_path,
                duration=duration if type in ["video", "audio"] else None
            )

        await ms.delete()
        os.remove(file_path)
        if ph_path:
            os.remove(ph_path)

    except Exception as e:
        logger.error(f"Error: {e}")

	    
