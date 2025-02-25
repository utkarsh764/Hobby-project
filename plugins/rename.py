import os
import time
import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, ForceReply
from pyrogram.errors import FloodWait
from config import LOG_CHANNEL  # Optional: For logging renamed files

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 2000 * 1024 * 1024  # 2GB

class RenamePlugin:
    def __init__(self):
        self.pending_rename_requests = {}  # Store user ID and file metadata for pending rename requests

    async def show_progress(self, current, total, start_time, operation):
        """Show a progress bar with circles and dots, and estimated time remaining."""
        elapsed_time = time.time() - start_time
        speed = current / elapsed_time if elapsed_time > 0 else 0  # Bytes per second
        remaining_bytes = total - current
        remaining_time = remaining_bytes / speed if speed > 0 else 0  # Estimated time in seconds

        # Convert bytes to MB
        current_mb = current / (1024 * 1024)
        total_mb = total / (1024 * 1024)

        # Progress bar (10 circles and dots)
        progress = min(current / total, 1.0)
        bar_length = 10
        filled_length = int(bar_length * progress)
        bar = "●" * filled_length + "○" * (bar_length - filled_length)

        # Estimated time remaining
        minutes, seconds = divmod(int(remaining_time), 60)
        time_remaining = f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s"

        # Progress message
        progress_message = (
            f"**🛠️ {operation.capitalize()} Progress...**\n"
            f"╭───────────⍟\n"
            f"`[{bar}]` {int(progress * 100)}%\n"
            f"├**{current_mb:.2f}MB / {total_mb:.2f}MB**\n"
            f"├**⏳ Estimated Time :** `{time_remaining}`"
            f"╰───────────────⍟"
        )
        return progress_message

    async def handle_rename_request(self, client: Client, message: Message):
        """Handle the rename request when user replies with /rename."""
        user_id = message.from_user.id
        file = getattr(message, message.media.value)  # Get the file (document, audio, or video)
        filename = file.file_name

        # Check file size
        if file.file_size > MAX_FILE_SIZE:
            return await message.reply_text("Sᴏʀʀy Bʀᴏ Tʜɪꜱ Bᴏᴛ Iꜱ Dᴏᴇꜱɴ'ᴛ Sᴜᴩᴩᴏʀᴛ Uᴩʟᴏᴀᴅɪɴɢ Fɪʟᴇꜱ Bɪɢɢᴇʀ Tʜᴀɴ 2Gʙ")

        # Store the file metadata for the user
        self.pending_rename_requests[user_id] = {
            "file_id": file.file_id,
            "file_name": filename,
            "media_type": message.media.value,
        }

        # Ask the user for the new filename
        try:
            await message.reply_text(
                text=f"**__Pʟᴇᴀꜱᴇ Eɴᴛᴇʀ Nᴇᴡ Fɪʟᴇɴᴀᴍᴇ...__**\n\n**Oʟᴅ Fɪʟᴇ Nᴀᴍᴇ** :- `{filename}`",
                reply_to_message_id=message.id,
                reply_markup=ForceReply(True),
            )
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await message.reply_text(
                text=f"**__Pʟᴇᴀꜱᴇ Eɴᴛᴇʀ Nᴇᴡ Fɪʟᴇɴᴀᴍᴇ...__**\n\n**Oʟᴅ Fɪʟᴇ Nᴀᴍᴇ** :- `{filename}`",
                reply_to_message_id=message.id,
                reply_markup=ForceReply(True),
            )
        except Exception as e:
            logger.error(f"Error while asking for new filename: {e}")
            await message.reply_text("❌ An error occurred. Please try again.")

    async def handle_new_filename(self, client: Client, message: Message):
        """Handle the new filename provided by the user."""
        user_id = message.from_user.id

        # Check if the user has a pending rename request
        if user_id not in self.pending_rename_requests:
            return

        new_filename = message.text.strip()
        if not new_filename:
            await message.reply_text("❌ Filename cannot be empty. Please try again.")
            return

        # Get the file metadata
        file_data = self.pending_rename_requests[user_id]
        file_id = file_data["file_id"]
        old_filename = file_data["file_name"]
        media_type = file_data["media_type"]

        # Preserve the original file extension
        original_extension = os.path.splitext(old_filename)[1]
        new_filename = os.path.splitext(new_filename)[0] + original_extension

        # Download the file
        try:
            progress_message = await message.reply_text("**🛠️ Downloading your file... Please wait...**")
            start_time = time.time()
            file_path = await client.download_media(
                file_id,
                file_name=old_filename,
                progress=lambda current, total: asyncio.create_task(
                    self.show_progress(current, total, start_time, "download")
                ),
            )
            await progress_message.delete()
        except Exception as e:
            logger.error(f"Error while downloading file: {e}")
            await message.reply_text("❌ Failed to download the file. Please try again.")
            return

        # Rename the file
        try:
            new_file_path = os.path.join(os.path.dirname(file_path), new_filename)
            os.rename(file_path, new_file_path)

            # Upload the renamed file using Telegram's native upload (supports up to 2GB)
            progress_message = await message.reply_text("**🛠️ Uploading your renamed file... Please wait...**")
            start_time = time.time()
            await client.send_document(
                chat_id=message.chat.id,
                document=new_file_path,
                caption=f"**📄 Renamed File:** `{new_filename}`",
                force_document=True,  # Ensures the file is uploaded as a document
                progress=lambda current, total: asyncio.create_task(
                    self.show_progress(current, total, start_time, "upload")
                ),
            )
            await progress_message.delete()

            # Log the renamed file (optional)
            if LOG_CHANNEL:
                await client.send_document(
                    chat_id=LOG_CHANNEL,
                    document=new_file_path,
                    caption=f"**📄 Renamed File from [{message.from_user.first_name}](tg://user?id={user_id})\nOld Name:** `{old_filename}`\n**New Name:** `{new_filename}`",
                )

            # Clean up
            os.remove(new_file_path)
        except Exception as e:
            logger.error(f"Error while renaming/uploading file: {e}")
            await message.reply_text("❌ Failed to rename/upload the file. Please try again.")
        finally:
            # Remove the user's pending request
            self.pending_rename_requests.pop(user_id, None)

# Initialize the plugin
rename_plugin = RenamePlugin()

# Register handlers
@Client.on_message(filters.private & (filters.document | filters.audio | filters.video) & filters.command("rename"))
async def rename_handler(client: Client, message: Message):
    await rename_plugin.handle_rename_request(client, message)

@Client.on_message(filters.private & filters.text & filters.reply)
async def new_filename_handler(client: Client, message: Message):
    # Check if the reply is to a ForceReply message
    if message.reply_to_message and message.reply_to_message.reply_markup and isinstance(message.reply_to_message.reply_markup, ForceReply):
        await rename_plugin.handle_new_filename(client, message)

