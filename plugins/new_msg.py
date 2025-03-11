from pyrogram import Client, filters
from config import API_ID, API_HASH, BOT_TOJEN
from helper.database import db

# Command to add the channel (Only works if sent in a channel)
@Client.on_message(filters.command("add") & filters.channel)
async def add_channel(client, message):
    channel_id = message.chat.id
    added = await db.add_channel(channel_id)  # Using the new database function

    if added:
        await message.reply("✅ Channel added! Now, all messages will be formatted.")
    else:
        await message.reply("ℹ️ This channel is already added.")

# Command to remove the channel (Only works if sent in a channel)
@Client.on_message(filters.command("rem") & filters.channel)
async def remove_channel(client, message):
    channel_id = message.chat.id
    if await db.is_channel_exist(channel_id):  # Check if the channel exists
        await db.remove_channel(channel_id)
        await message.reply("❌ Channel removed! Messages will no longer be formatted.")
    else:
        await message.reply("ℹ️ This channel is not in the list.")

# Automatically format messages in added channels
@Client.on_message(filters.channel)
async def format_message(client, message):
    channel_id = message.chat.id
    if await db.is_channel_exist(channel_id):  # Check if channel is in the database
        if message.text and not message.text.startswith("/"):  # Ignore commands
            formatted_text = f"```\n{message.text}\n```"
            await message.edit_text(formatted_text)  # Edit message with formatting
