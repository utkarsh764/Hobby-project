from pyrogram import Client, filters
from helper.database import db
import asyncio


# ✅ Store Channel When /code is Sent
@Client.on_message(filters.command("add") & filters.chat_type.groups)
async def add_channel(client, message):
    channel_id = message.chat.id
    added = await db.add_channel(channel_id)

    if added:
        await message.reply_text("✅ This channel is now registered for message formatting.")
    else:
        await message.reply_text("⚠️ This channel is already registered.")


# ❌ Remove Channel When /rem is Sent
@Client.on_message(filters.command("rem") & filters.chat_type.groups)
async def remove_channel(client, message):
    channel_id = message.chat.id
    exists = await db.is_channel_exist(channel_id)

    if exists:
        await db.remove_channel(channel_id)
        await message.reply_text("✅ This channel has been removed from formatting.")
    else:
        await message.reply_text("⚠️ This channel is not registered.")


# 🔄 Format Messages in Stored Channels
@Client.on_message(filters.group)
async def format_channel_messages(client, message):
    channel_id = message.chat.id
    is_registered = await db.is_channel_exist(channel_id)

    if is_registered and message.text:
        formatted_text = f"```{message.text}```"
        try:
            await asyncio.sleep(1)  # Delay to avoid errors
            await message.edit_text(formatted_text)  # Edit message with formatted text
        except Exception as e:
            print(f"Error editing message: {e}")


# 📨 Format Messages in DM When User Replies with /code
@Client.on_message(filters.command("add") & filters.private & filters.reply)
async def format_dm_message(client, message):
    if message.reply_to_message and message.reply_to_message.text:
        formatted_text = f"```{message.reply_to_message.text}```"
        await message.reply_text(formatted_text)
    else:
        await message.reply_text("⚠️ This command works only when replying to a text message.")

