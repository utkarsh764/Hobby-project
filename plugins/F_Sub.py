import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import UserNotParticipant
from config import *

@Client.on_message(filters.private & filters.incoming)
async def forcesub(c, m):
    owner = await c.get_users(int(ADMIN))
    if UPDATE_CHANNEL:
        try:
            user = await c.get_chat_member(UPDATE_CHANNEL, m.from_user.id)
            if user.status == "kicked":
               await m.reply_text("**Yᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ɪɴ Oᴜʀ ᴄʜᴀɴɴᴇʟ Cᴏɴᴛᴀᴄᴛ Aᴅᴍɪɴ 😜**", quote=True)
               return
        except UserNotParticipant:
            buttons = [[InlineKeyboardButton(text='Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ 🔖', url=f"https://t.me/{UPDATE_CHANNEL}")]]
            if m.text:
                if (len(m.text.split(' ')) > 1) & ('start' in m.text):
                    chat_id, msg_id = m.text.split(' ')[1].split('_')
                    buttons.append([InlineKeyboardButton('🔄 Rᴇғʀᴇsʜ', callback_data=f'refresh+{chat_id}+{msg_id}')])
            await m.reply_text(
                f"Hey {m.from_user.mention(style='md')} ʏᴏᴜ ɴᴇᴇᴅ ᴊᴏɪɴ Mʏ ᴜᴘᴅᴀᴛᴇs ᴄʜᴀɴɴᴇʟ ɪɴ ᴏʀᴅᴇʀ ᴛᴏ ᴜsᴇ ᴍᴇ 😉\n\n"
                "__Pʀᴇss ᴛʜᴇ Fᴏʟʟᴏᴡɪɴɢ Bᴜᴛᴛᴏɴ ᴛᴏ ᴊᴏɪɴ Nᴏᴡ 👇__",
                reply_markup=InlineKeyboardMarkup(buttons),
                quote=True
            )
            return
        except Exception as e:
            print(e)
            await m.reply_text(f"Sᴏᴍᴇᴛʜɪɴɢ Wʀᴏɴɢ. Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ ᴏʀ ᴄᴏɴᴛᴀᴄᴛ {owner.mention(style='md')}", quote=True)
            return
    await m.continue_propagation()


@Client.on_callback_query(filters.regex('^refresh'))
async def refresh_cb(c, m):
    owner = await c.get_users(int(ADMIN))
    if UPDATE_CHANNEL:
        try:
            user = await c.get_chat_member(UPDATE_CHANNEL, m.from_user.id)
            if user.status == "kicked":
               try:
                   await m.message.edit("**Yᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ɪɴ Oᴜʀ ᴄʜᴀɴɴᴇʟ Cᴏɴᴛᴀᴄᴛ Aᴅᴍɪɴ 😜**")
               except:
                   pass
               return
        except UserNotParticipant:
            await m.answer('Yᴏᴜ ᴀʀᴇ ɴᴏᴛ ʏᴇᴛ ᴊᴏɪɴᴇᴅ ᴏᴜʀ ᴄʜᴀɴɴᴇʟ. \nFɪʀsᴛ ᴊᴏɪɴ ᴀɴᴅ ᴛʜᴇɴ ᴘʀᴇss ʀᴇғʀᴇsʜ ʙᴜᴛᴛᴏɴ ', show_alert=True)
            return
        except Exception as e:
            print(e)
            await m.message.edit(f"Sᴏᴍᴇᴛʜɪɴɢ Wʀᴏɴɢ. Pʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ ᴏʀ ᴄᴏɴᴛᴀᴄᴛ{owner.mention(style='md')}")
            return

    
