from asyncio import sleep
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from config import START_PIC, ADMIN
from helper.txt import mr
from helper.database import db

# Start Command
@Client.on_message(filters.private & filters.command("start"))
async def start(client, message):
    user = message.from_user
    if not await db.is_user_exist(user.id):
        await db.add_user(user.id)
    
    txt = (f"**👋 Hello {user.mention}**\n\n"
           "I am an advanced file Renamer and Converter BOT with permanent and custom thumbnail support.\n\n"
           "Send me any video or document!")
    
    button = InlineKeyboardMarkup([
        [InlineKeyboardButton("🤖 Developer", url='https://t.me/axa_bachha')],
        [InlineKeyboardButton('⚡️ About', callback_data='about'),
         InlineKeyboardButton('🤕 Help', callback_data='help')]
    ])
    
    if START_PIC:
        await message.reply_photo(START_PIC, caption=txt, reply_markup=button)
    else:
        await message.reply_text(text=txt, reply_markup=button, disable_web_page_preview=True)

# Logs Command
@Client.on_message(filters.command('logs') & filters.user(ADMIN))
async def log_file(client, message):
    try:
        await message.reply_document('TelegramBot.log')
    except Exception as e:
        await message.reply_text(f"Error:\n`{e}`")

# Callback Query Handler
@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    data = query.data
    
    if data == "start":
        txt = (f"**👋 Hello {query.from_user.mention}**\n\n"
               "I am an advanced file Renamer and Converter BOT with permanent and custom thumbnail support.\n\n"
               "Send me any video or document!")
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🤖 Developer", url='https://t.me/axa_bachha')],
            [InlineKeyboardButton('⚡️ About', callback_data='about'),
             InlineKeyboardButton('🤕 Help', callback_data='help')]
        ])
    
    elif data == "help":
        txt = mr.HELP_TXT
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("ᴄᴏɴᴛᴀᴄᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ 🕵🏻‍♀️", url="https://t.me/axa_bachha")],
            [InlineKeyboardButton("ʀᴇᴏ̨ᴜᴇsᴛ ᴀᴄᴄᴇᴘᴛᴏʀ", callback_data="request"),
            InlineKeyboardButton("ᴍᴇʀɢᴇ 📄", callback_data="combiner")],
            [InlineKeyboardButton("ʀᴇsᴛʀɪᴄᴛᴇᴅ ᴄᴏɴᴛᴇɴᴛ sᴀᴠᴇʀ", callback_data="restricted")],
            [ 
             InlineKeyboardButton('ᴛᴇʟᴇɢʀᴀᴘʜ', callback_data='tele'),   
             InlineKeyboardButton('ꜱᴛɪᴄᴋᴇʀ-ɪᴅ', callback_data='sticker') 
         ], [             
             InlineKeyboardButton('🏠 𝙷𝙾𝙼𝙴 🏠', callback_data='start')
        ]
        ])
    
    elif data == "about":
        txt = mr.ABOUT_TXT.format(client.mention)
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("❣️ Developer ❣️", url="https://t.me/axa_bachha")],
            [InlineKeyboardButton("🔒 Close", callback_data="close"),
             InlineKeyboardButton("◀️ Back", callback_data="start")]
        ])
    
    elif data == "close":
        try:
            await query.message.delete()
            await query.message.reply_to_message.delete()
        except:
            await query.message.delete()
        return
    
    await query.message.edit_text(text=txt, reply_markup=reply_markup, disable_web_page_preview=True)
    
    elif query.data == "sticker":
        btn = [[
            InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="help"),
            InlineKeyboardButton("Cᴏɴᴛᴀᴄᴛ", url="telegram.me/axa_bachha")
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(btn)
        await query.message.edit_text(
            text=(STICKER_TXT),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )


    elif query.data == "tele":
        btn = [[
            InlineKeyboardButton("⟸ Bᴀᴄᴋ", callback_data="help"),
            InlineKeyboardButton("Cᴏɴᴛᴀᴄᴛ", url="telegram.me/axa_bachha")
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(btn)
        await query.message.edit_text(
            text=(TELE_TXT),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )


# Additional Callback Queries
CALLBACK_TEXTS = {
    "restricted": "> **💡 Restricted Content Saver**\n\n"
                   "**1. 🔒 Private Chats**\n➥ Send the invite link (if not already a member).\n➥ Send the post link to download content.\n\n"
                   "**2. 🌐 Public Chats**\n➥ Simply share the post link.\n\n"
                   "**3. 📂 Batch Mode**\n➥ Download multiple posts using this format: \n"
                   "https://t.me/xxxx/1001-1010",

    "combiner": "> **⚙️ PDF Merging**\n\n"
                 "📄 **/merge** - Start the merging process.\n"
                 "⏳ **Upload PDFs or Images in sequence.**\n"
                 "✅ **Type /done** to merge into a single PDF.\n\n"
                 "> 🌺 **Supported Files:**\n"
                 "• 📑 PDFs: Up to 20 files.\n"
                 "• 🖼️ Images: Convert images to PDF.\n\n"
                 "> ⚠️ **Restrictions:**\n"
                 "• Max File Size: 20MB\n"
                 "• Max Files per Merge: 20\n\n"
                 "> ✨ **Customizations:**\n"
                 "• 📝 Filename: Provide a custom name.\n"
                 "• 📸 Thumbnail: Use (Filename) -t (Thumbnail link).",

    "request": "> **⚙️ Join Request Acceptor**\n\n"
                "• I can accept all pending join requests in your channel. 🤝\n\n"
                "• Promote @Axa_bachha and @Z900_RoBot with full admin rights in your channel. 🔑\n\n"
                "• Send /accept command to start accepting join requests. ▶️"
}

@Client.on_callback_query(filters.regex("restricted|combiner|request"))
async def callback_text_handler(client: Client, query: CallbackQuery):
    await query.answer()
    await query.message.edit_text(
        text=CALLBACK_TEXTS[query.data],
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="help")]
        ]),
        disable_web_page_preview=True
    )


    TELE_TXT = """<b>ʜᴇʟᴘ: ᴛᴇʟᴇɢʀᴀᴘʜ ᴅᴏ ᴀꜱ ʏᴏᴜ ᴡɪꜱʜ ᴡɪᴛʜ ᴛᴇʟᴇɢʀᴀ.ᴘʜ ᴍᴏᴅᴜʟᴇ! 
  
 ᴜꜱᴀɢᴇ: /telegraph - ꜱᴇɴᴅ ᴍᴇ ᴘɪᴄᴛᴜʀᴇ ᴏʀ ᴠɪᴅᴇ ᴜɴᴅᴇʀ (5ᴍʙ) 
  
 ɴᴏᴛᴇ: 
 ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ɪꜱ ᴀᴠᴀɪʟᴀʙʟᴇ ɪɴ ɢᴏᴜᴘꜱ ᴀɴᴅ ᴘᴍꜱ 
 ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴄᴀɴ ʙᴇ ᴜꜱᴇᴅ ʙʏ ᴇᴠᴇʀʏᴏɴᴇ</b>""" 

    STICKER_TXT = """<b>yᴏᴜ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴍᴏᴅᴜʟᴇ ᴛᴏ ꜰɪɴᴅ ᴀɴy  ꜱᴛɪᴄᴋᴇʀꜱ ɪᴅ. 
 • ᴜꜱᴀɢᴇ :ᴛᴏ ɢᴇᴛ ꜱᴛɪᴄᴋᴇʀ 
   
 ⭕ ʜᴏᴡ ᴛᴏ ᴜꜱᴇ 
 /stickerid
 </b>""" 
