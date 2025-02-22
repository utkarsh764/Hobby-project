from asyncio import sleep
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, CallbackQuery
from pyrogram.errors import FloodWait
import humanize
import random
from helper.txt import mr
from helper.database import db
from config import START_PIC, FLOOD, ADMIN 


@Client.on_message(filters.private & filters.command(["start"]))
async def start(client, message):
    user = message.from_user
    if not await db.is_user_exist(user.id):
        await db.add_user(user.id)             
    txt=f"**👋 Hello Developer {user.mention} \n\nI am an Advance file Renamer and file Converter BOT with permanent and custom thumbnail support.\n\nSend me any video or document !**"
    button=InlineKeyboardMarkup([[
        InlineKeyboardButton("🤖 Developer ", url='https://t.me/axa_bachha')
        ],[
        InlineKeyboardButton('⚡️ About', callback_data='about'),
        InlineKeyboardButton('🤕 Help', callback_data='help')
    ]
        ])
    if START_PIC:
        await message.reply_photo(START_PIC, caption=txt, reply_markup=button)       
    else:
        await message.reply_text(text=txt, reply_markup=button, disable_web_page_preview=True)
    

@Client.on_message(filters.command('logs') & filters.user(ADMIN))
async def log_file(client, message):
    try:
        await message.reply_document('TelegramBot.log')
    except Exception as e:
        await message.reply_text(f"Error:\n`{e}`")


@Client.on_callback_query()
async def cb_handler(client, query: CallbackQuery):
    data = query.data 
    if data == "start":
        await query.message.edit_text(
            text=f"""**👋 Hello Developer {query.from_user.mention} \n\nI am an Advance file Renamer and file Converter BOT with permanent and custom thumbnail support.\n\nSend me any video or document !**""",
            reply_markup=InlineKeyboardMarkup( [[        
        InlineKeyboardButton("🤖 Developer ", url='https://t.me/axa_bachha')
        ],[
        InlineKeyboardButton('⚡️ About', callback_data='about'),
        InlineKeyboardButton('🤕 Help', callback_data='help')
    ]
        ]
                )
            )
    elif data == "help":
        await query.message.edit_text(
            text=mr.HELP_TXT,
            reply_markup=InlineKeyboardMarkup( [               
                [InlineKeyboardButton("❣️ Contact Admin ❣️", url="https://t.me/axa_bachha")],
                [InlineKeyboardButton("• Join Request acceptor •", callback_data="request")],
                [InlineKeyboardButton("📃 PDF Merging 📃", callback_data="combiner")],
                [InlineKeyboardButton("🪄 Restricted content saver 🪄", callback_data=")],
                [InlineKeyboardButton("🔒 𝙲𝙻𝙾𝚂𝙴", callback_data = "close"),
               InlineKeyboardButton("◀️ 𝙱𝙰𝙲𝙺", callback_data = "start")
               ]]
            )
        )
    elif data == "about":
        await query.message.edit_text(
            text=mr.ABOUT_TXT.format(client.mention),
            disable_web_page_preview = True,
            reply_markup=InlineKeyboardMarkup( [[
               #⚠️ don't change source code & source link ⚠️ #
               InlineKeyboardButton("❣️ Developer ❣️", url="https://t.me/axa_bachha")
               ],[
               InlineKeyboardButton("🔒 𝙲𝙻𝙾𝚂𝙴", callback_data = "close"),
               InlineKeyboardButton("◀️ 𝙱𝙰𝙲𝙺", callback_data = "start")
               ]]
            )
        )

    
    elif data == "close":
        try:
            await query.message.delete()
            await query.message.reply_to_message.delete()
        except:
            await query.message.delete()
            

RESTRICTED_TXT = """> **💡 Restricted content saver**

**1. 🔒 Private Chats**
➥ Send the invite link (if not already a member).  
➥ Send the post link to download content.

**2. 🌐 Public Chats**
➥ Simply share the post link.

**3. 📂 Batch Mode**
➥ Download multiple posts using this format:  
> https://t.me/xxxx/1001-1010"""

#------------------- MERGE -------------------#

MERGER_TXT = """> **⚙️ Hᴇʟᴘ Dᴇsᴄʀɪᴘᴛɪᴏɴ ⚙️**

📄 **/merge** - Start the merging process.  
⏳ **Upload your files (PDFs or Images) in sequence.**  
✅ **Type /done** to merge the uploaded files into a single PDF.

> 🌺 **Supported Files:**  
**• 📑 PDFs: Add up to 20 PDF files.**
**• 🖼️ Images: Convert images to PDF pages.**

> ⚠️ **Restrictions:**  
**• Max File Size: 20MB**
**• Max Files per Merge: 20**

> ✨ **Customizations:**  
**• 📝 Filename: Provide a custom name for your PDF.**
**• 📸 Thumbnail: Use (Filename) -t (Thumbnail link).**"""

#--------------------------------------------------------

@Client.on_callback_query(filters.regex("restricted"))
async def restricted_callback(client: Client, callback_query):
    await callback_query.answer()  # Acknowledge the callback
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="help")]
    ])
    await callback_query.message.edit_text(
        RESTRICTED_TXT,
        reply_markup=reply_markup
    )

@Client.on_callback_query(filters.regex("combiner"))
async def combiner_callback(client: Client, callback_query):
    await callback_query.answer()  # Acknowledge the callback
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="help")]
    ])
    await callback_query.message.edit_text(
        MERGER_TXT,
        reply_markup=reply_markup
    )

@Client.on_callback_query(filters.regex("request"))
async def request_info_callback(client: Client, callback_query):
    try:
        await callback_query.answer()  # Acknowledge the callback
        logger.info(f"Request callback triggered by {callback_query.from_user.id}")  # Log the callback query
        request_text = (
            f"> **⚙️ Join request acceptor**\n\n"
            "**• I can accept all pending join requests in your channel. 🤝**\n\n"
            "**• Promote @Axa_bachha and @Z900_RoBot with full admin rights in your channel. 🔑**\n\n"
            "**• Send /accept command to start accepting join requests. ▶️**"
        )
        reply_markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔙 Back", callback_data="help")
            ]
        ])
        await callback_query.message.edit_text(
            request_text, 
            reply_markup=reply_markup, 
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.error(f"Error in 'request_info_callback': {e}")
        await callback_query.answer("An error occurred. Please try again later.", show_alert=True)
      
