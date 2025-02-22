from pyrogram import Client, filters

@Client.on_message(filters.command("stickerid") & filters.reply)
async def stickerid(bot, message):
    replied_msg = message.reply_to_message
    
    if replied_msg and replied_msg.sticker:
        await message.reply_text(
            f"🆔 **Sticker ID:**  \n\n`{replied_msg.sticker.file_id}`\n\n"
            f"🔑 **Unique ID:** `{replied_msg.sticker.file_unique_id}`"
        )
    else:
        await message.reply_text("ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ sᴛɪᴄᴋᴇʀ ᴡɪᴛʜ /stickerid 🖼️")
