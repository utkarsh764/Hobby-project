import os
import time
import asyncio
import logging
import datetime
from config import ADMIN
from helper.database import db
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@Client.on_message(filters.command("users") & filters.user(ADMIN))
async def get_stats(bot: Client, message: Message):
    mr = await message.reply('**𝙰𝙲𝙲𝙴𝚂𝚂𝙸𝙽𝙶 𝙳𝙴𝚃𝙰𝙸𝙻𝚂.....**')
    total_users = await db.total_users_count()
    await mr.edit(text=f"**❤️‍🔥 TOTAL USERS = {total_users}**")

@Client.on_message(filters.command("broadcast") & filters.user(ADMIN) & filters.reply)
async def broadcast_handler(bot: Client, m: Message):
    all_users = await db.get_all_users()
    broadcast_msg = m.reply_to_message
    sts_msg = await m.reply_text("Broadcast started!")
    
    done, failed, success = 0, 0, 0
    start_time = time.time()
    total_users = await db.total_users_count()

    async for user in all_users:
        sts = await send_msg(bot, user['_id'], broadcast_msg)
        if sts == 200:
            success += 1
        else:
            failed += 1
        if sts == 400:
            await db.delete_user(user['_id'])

        done += 1
        if not done % 20:
            await sts_msg.edit(
                f"**Broadcast in progress:\nTotal Users: {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nFailed: {failed}**"
            )

    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await sts_msg.edit(
        f"**Broadcast Completed:\nCompleted in `{completed_in}`.\n\nTotal Users: {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nFailed: {failed}**"
    )

async def send_msg(bot, user_id, message):
    try:
        sent_msg = await message.copy(chat_id=int(user_id))
        await db.add_broadcast_message(user_id, sent_msg.message_id)  # Store message ID
        return 200
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await send_msg(bot, user_id, message)
    except InputUserDeactivated:
        logger.info(f"{user_id} : deactivated")
        return 400
    except UserIsBlocked:
        logger.info(f"{user_id} : blocked the bot")
        return 400
    except PeerIdInvalid:
        logger.info(f"{user_id} : user id invalid")
        return 400
    except Exception as e:
        logger.error(f"{user_id} : {e}")
        return 500


@Client.on_message(filters.private & filters.command('dbroadcast') & filters.user(ADMIN) & filters.reply)
async def delete_broadcast(client: Bot, message: Message):
    if message.reply_to_message:
        try:
            duration = int(message.command[1])  # Get the duration in seconds
        except (IndexError, ValueError):
            await message.reply("<b>Please provide a valid duration in seconds.</b> Usage: /dbroadcast {duration}")
            return

        query = await full_userbase()
        broadcast_msg = message.reply_to_message
        total = 0
        successful = 0
        blocked = 0
        deleted = 0
        unsuccessful = 0

        pls_wait = await message.reply("<i>Broadcast with auto-delete processing....</i>")
        for chat_id in query:
            try:
                sent_msg = await broadcast_msg.copy(chat_id)
                await asyncio.sleep(duration)  # Wait for the specified duration
                await sent_msg.delete()  # Delete the message after the duration
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.x)
                sent_msg = await broadcast_msg.copy(chat_id)
                await asyncio.sleep(duration)
                await sent_msg.delete()
                successful += 1
            except UserIsBlocked:
                await del_user(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await del_user(chat_id)
                deleted += 1
            except:
                unsuccessful += 1
                pass
            total += 1

        status = f"""<b><u>Broadcast with Auto-Delete...</u>

Total Users: <code>{total}</code>
Successful: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code></b>"""

        return await pls_wait.edit(status)

    else:
        msg = await message.reply("Please reply to a message to broadcast it with auto-delete.")
        await asyncio.sleep(8)
        await msg.delete()

