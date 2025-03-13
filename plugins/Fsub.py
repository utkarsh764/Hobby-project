from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant
from config import *

#=====================================================================================

@Client.on_message(filters.private & filters.command)
async def check_subscription(client, message):
    """
    Checks if the user is subscribed before processing any command.
    """
    if AUTH_CHANNEL:
        btn = await is_subscribed(client, message.from_user.id, AUTH_CHANNEL)
        if btn:  # If user is not subscribed
            username = (await client.get_me()).username
            start_param = message.command[1] if len(message.command) > 1 else "true"
            btn.append([InlineKeyboardButton("🔄 Rᴇғʀᴇsʜ", url=f"https://t.me/{username}?start={start_param}")])

            await message.reply_photo(
                    photo=FORCE_PIC,  # Using the variable FORCE_PIC
                    caption=f"<b>👋 Hello {message.from_user.mention},\nʏᴏᴜ ɴᴇᴇᴅ ᴊᴏɪɴ Mʏ ᴜᴘᴅᴀᴛᴇs ᴄʜᴀɴɴᴇʟ ɪɴ ᴏʀᴅᴇʀ ᴛᴏ ᴜsᴇ ᴍᴇ 😉\n\nPʀᴇss ᴛʜᴇ Fᴏʟʟᴏᴡɪɴɢ Bᴜᴛᴛᴏɴ ᴛᴏ ᴊᴏɪɴ Nᴏᴡ 👇</b>",
                    reply_markup=InlineKeyboardMarkup(btn)
            )
            return  # Stop further execution

    await client.process_message(message)  # Continue normal execution if user is subscribed
        
#=====================================================================================
async def is_subscribed(bot, query, channel):
    btn = []
    for id in channel:
        chat = await bot.get_chat(int(id))
        try:
            await bot.get_chat_member(id, query.from_user.id)
        except UserNotParticipant:
            btn.append([InlineKeyboardButton(f'Join {chat.title}', url=chat.invite_link)])
        except Exception as e:
            pass
    return btn
  
