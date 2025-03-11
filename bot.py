import logging
import logging.config
import asyncio
from pyrogram import Client
from pyrogram.enums import ParseMode
from aiohttp import web
from datetime import datetime
import sys
from config import *
from plugins.web_support import web_server

logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)


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

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.mention = me.mention
        self.username = me.username
        self.uptime = datetime.now()

        # Force Subscription Logic for 4 Channels
        for index, channel in enumerate([FORCE_SUB_CHANNEL1, FORCE_SUB_CHANNEL2, FORCE_SUB_CHANNEL3, FORCE_SUB_CHANNEL4], start=1):
            if channel:
                try:
                    link = (await self.get_chat(channel)).invite_link
                    if not link:
                        await self.export_chat_invite_link(channel)
                        link = (await self.get_chat(channel)).invite_link
                    setattr(self, f"invitelink{index}", link)
                except Exception as e:
                    logging.warning(e)
                    logging.warning(f"Bot can't export invite link for FORCE_SUB_CHANNEL{index}!")
                    logging.warning(f"Make sure bot is admin in the channel with 'Invite Users via Link' permission.")
                    sys.exit()

        # Start Web Server
        app = web.AppRunner(await web_server())
        await app.setup()
        await web.TCPSite(app, "0.0.0.0", PORT).start()

        # Notify Owner
        try:
            await self.send_message(ADMIN, text=f"<b><blockquote>🤖 Bot Restarted!</blockquote></b>")
        except Exception as e:
            logging.warning(f"Failed to notify owner: {e}")

        logging.info(f"{me.first_name} ✅✅ Bot started successfully ✅✅")

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot Stopped 🙄")

bot = Bot()
bot.run()
