import logging
import logging.config
from pyrogram import Client, filters, enums
from pyrogram.errors import UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import API_ID, API_HASH, BOT_TOKEN, FORCE_SUB, PORT
from aiohttp import web
from plugins.web_support import web_server

#
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)


async def not_subscribed(_, client, message):
    if not client.force_channel:
        return False  # Skip check if no force channel is set    
    try:
        user = await client.get_chat_member(client.force_channel, message.from_user.id)
        if user.status == enums.ChatMemberStatus.BANNED:
            return True  # Treat banned users as not subscribed
        return False
    except UserNotParticipant:
        return True 
    except Exception as e:
        logging.error(f"Error checking subscription: {e}")
        return False 

class Bot(Client):

    def __init__(self):
        super().__init__(
            name="renamer",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=50,
            plugins={"root": "plugins"},
            sleep_threshold=5,
        )
        self.force_channel = None
        self.invitelink = None

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.mention = me.mention
        self.username = me.username 
        self.force_channel = FORCE_SUB
        if FORCE_SUB:
            try:
                link = await self.export_chat_invite_link(FORCE_SUB)                  
                self.invitelink = link
            except Exception as e:
                logging.warning(e)
                logging.warning("Make Sure Bot admin in force sub channel")             
                self.force_channel = None
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, PORT).start()
        logging.info(f"{me.first_name} ✅✅ BOT started successfully ✅✅")

    async def stop(self, *args):
        await super().stop()      
        logging.info("Bot Stopped 🙄")

    # Handler for non-subscribed users
    @Client.on_message(filters.private & filters.create(not_subscribed))
    async def is_not_subscribed(self, message):
        join_message = "**𝚂𝙾𝚁𝚁𝚈 𝙳𝚄𝙳𝙴 𝚈𝙾𝚄've 𝙽𝙾𝚃 𝙹𝙾𝙸𝙽𝙳 𝙼𝚈 𝙲𝙷𝙰𝙽𝙽𝙴𝙻 😔. 𝙿𝙻𝙴𝙰𝚂𝙴 𝙹𝙾𝙸𝙽 𝙼𝚈 𝙲𝙷𝙰𝙽𝙽𝙴𝙻 𝚃𝙾 𝚄𝚂𝙴 𝚃𝙷𝙸𝚂 𝙱𝙾𝚃. 🙏 **"        
        buttons = [
            [InlineKeyboardButton("📢 𝙹𝚘𝚒𝚗 𝙼𝚢 𝚄𝚙𝚍𝚊𝚝𝚎 𝙲𝚑𝚊𝚗𝚗𝚎𝚕 📢", url="self.invitelink")],
            [InlineKeyboardButton("🔄 Check Again 🔄", callback_data="check_subscription")]
        ]        
        await message.reply_text(
            text=join_message,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        
    @Client.on_callback_query(filters.regex("check_subscription"))
    async def check_subscription_callback(self, callback_query):
        user_id = callback_query.from_user.id
        
        try:
            user = await self.get_chat_member(self.force_channel, user_id)
            if user.status != enums.ChatMemberStatus.BANNED:
                # User is subscribed - trigger /start command
                await self.send_message(user_id, "/start")  # Trigger /start command
                return
        except UserNotParticipant:
            pass 
        join_message = "**𝚂𝙾𝚁𝚁𝚈 𝙳𝚄𝙳𝙴 𝚈𝙾𝚄've 𝙽𝙾𝚃 𝙹𝙾𝙸𝙽𝙳 𝙼𝚈 𝙲𝙷𝙰𝙽𝙽𝙴𝙻 😔. 𝙿𝙻𝙴𝙰𝚂𝙴 𝙹𝙾𝙸𝙽 𝙼𝚈 𝙲𝙷𝙰𝙽𝙽𝙴𝙻 𝚃𝙾 𝚄𝚂𝙴 𝚃𝙷𝙸𝚂 𝙱𝙾𝚃. 🙏 **"        
        buttons = [
            [InlineKeyboardButton("📢 𝙹𝚘𝚒𝚗 𝙼𝚢 𝚄𝚙𝚍𝚊𝚝𝚎 𝙲𝚑𝚊𝚗𝚗𝚎𝚕 📢", url="self.invitelink")],
            [InlineKeyboardButton("🔄 Check Again 🔄", callback_data="check_subscription")]
        ]        
        await callback_query.message.edit_text(
            text=join_message,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        
bot = Bot()
bot.run()
