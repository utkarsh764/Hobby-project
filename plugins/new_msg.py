from pyrogram import Client, filters
import os

# Automatically format all messages in a channel
@Client.on_message(filters.channel)
async def format_message(client, message):
    if message.text:  # Check if the message contains text
        formatted_text = f"```\n{message.text}\n```"
        await message.edit_text(formatted_text)  # Edit message with formatting
