import time
import math
import requests
import os
import re
import logging
import tempfile
import asyncio
from PIL import Image
from pyrogram import Client, filters
from PyPDF2 import PdfMerger
from pyrogram.types import Message
from config import LOG_CHANNEL

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

class MergePlugin:
    def __init__(self):
        self.pending_filename_requests = {}
        self.user_file_metadata = {}  # Store metadata for each user's files
        self.user_states = {}  # Track user states
        self.upload_start_time = {}  # Track upload start time for each user

    async def reset_user_state(self, user_id: int):
        await asyncio.sleep(120)  # 2 minutes
        if user_id in self.user_file_metadata:
            self.user_file_metadata.pop(user_id, None)
            self.pending_filename_requests.pop(user_id, None)
            self.user_states.pop(user_id, None)
            logger.info(f"Reset state for user {user_id} due to inactivity.")

    async def show_progress_bar(self, progress_message, current, total, action="Processing"):
        """Show upload progress in the specified format."""
        if user_id not in self.upload_start_time:
            self.upload_start_time[user_id] = time.time()

        elapsed_time = time.time() - self.upload_start_time[user_id]
        upload_speed = current / elapsed_time if elapsed_time > 0 else 0  # Bytes per second
        remaining_bytes = total - current
        remaining_time = remaining_bytes / upload_speed if upload_speed > 0 else 0  # Seconds

        # Convert upload speed to a readable format (e.g., KB/s, MB/s)
        if upload_speed < 1024:
            speed_str = f"{upload_speed:.2f} B/s"
        elif upload_speed < 1024 * 1024:
            speed_str = f"{upload_speed / 1024:.2f} KB/s"
        else:
            speed_str = f"{upload_speed / (1024 * 1024):.2f} MB/s"

        # Convert remaining time to a readable format (e.g., seconds, minutes)
        if remaining_time < 60:
            time_str = f"{int(remaining_time)}s"
        else:
            time_str = f"{int(remaining_time // 60)}m {int(remaining_time % 60)}s"

        # Calculate percentage
        percentage = (current / total) * 100

        # Format the progress message
        progress_text = f"""
╭━━━━❰ Uploading... ❱━➣
┣⪼ 🗂️ : {self.format_bytes(current)} | {self.format_bytes(total)}
┣⪼ ⏳️ : {percentage:.1f}%
┣⪼ 🚀 : {speed_str}
┣⪼ ⏱️ : {time_str}
╰━━━━━━━━━━━━━━━➣
"""
        await progress_message.edit_text(progress_text)

    def format_bytes(self, size: int) -> str:
        """Convert bytes to a human-readable format."""
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.2f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.2f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.2f} GB"

    async def start_file_collection(self, client: Client, message: Message):
        user_id = message.from_user.id
        self.user_file_metadata[user_id] = []  # Reset file list for the user
        self.user_states[user_id] = "collecting_files"  # Set user state
        await message.reply_text(
            "**📤 Uᴘʟᴏᴀᴅ ʏᴏᴜʀ ғɪʟᴇs ɪɴ sᴇǫᴜᴇɴᴄᴇ, ᴛʏᴘᴇ /done ✅, ᴀɴᴅ ɢᴇᴛ ʏᴏᴜʀ ᴍᴇʀɢᴇᴅ PDF !! 🧾**"
        )
        # Start a timer to reset the state after 2 minutes
        asyncio.create_task(self.reset_user_state(user_id))

    async def handle_pdf_metadata(self, client: Client, message: Message):
        user_id = message.from_user.id

        # Only accept PDFs if the user has started the merge process
        if user_id not in self.user_states or self.user_states[user_id] != "collecting_files":
            return

        if message.document.mime_type != "application/pdf":
            await message.reply_text("❌ This is not a valid PDF file. Please send a PDF 📑.")
            return

        if len(self.user_file_metadata[user_id]) >= 20:
            await message.reply_text("⚠️ You can upload up to 20 files. Type /done ✅ to merge them.")
            return

        if message.document.file_size > MAX_FILE_SIZE:
            await message.reply_text("🚫 File size is too large! Please send a file under 20MB.")
            return

        self.user_file_metadata[user_id].append(
            {
                "type": "pdf",
                "file_id": message.document.file_id,
                "file_name": message.document.file_name,
            }
        )
        await message.reply_text(
            f"**➕ PDF ᴀᴅᴅᴇᴅ ᴛᴏ ᴛʜᴇ ʟɪsᴛ! 📄 ({len(self.user_file_metadata[user_id])} files added so far.)**\n"
            "**Sᴇɴᴅ ᴍᴏʀᴇ ғɪʟᴇs ᴏʀ ᴜsᴇ /done ✅ ᴛᴏ ᴍᴇʀɢᴇ ᴛʜᴇᴍ.**"
        )

    async def handle_image_metadata(self, client: Client, message: Message):
        user_id = message.from_user.id

        # Only accept images if the user has started the merge process
        if user_id not in self.user_states or self.user_states[user_id] != "collecting_files":
            return

        self.user_file_metadata[user_id].append(
            {
                "type": "image",
                "file_id": message.photo.file_id,
                "file_name": f"photo_{len(self.user_file_metadata[user_id]) + 1}.jpg",
            }
        )
        await message.reply_text(
            f"➕ Image added to the list! 🖼️ ({len(self.user_file_metadata[user_id])} files added so far.)\n"
            "Send more files or use /done ✅ to merge them."
        )

    async def merge_files(self, client: Client, message: Message):
        user_id = message.from_user.id

        if user_id not in self.user_file_metadata or not self.user_file_metadata[user_id]:
            await message.reply_text("**⚠️ Yᴏᴜ ʜᴀᴠᴇɴ'ᴛ ᴀᴅᴅᴇᴅ ᴀɴʏ ғɪʟᴇs ʏᴇᴛ. Usᴇ /merge ᴛᴏ sᴛᴀʀᴛ.**")
            return

        await message.reply_text("**✍️ Type a name for your merged PDF 📄.**")
        self.user_states[user_id] = "waiting_for_filename"  # Set user state

    async def handle_filename(self, client: Client, message: Message):
        user_id = message.from_user.id

        # Only process if the user is in the "waiting_for_filename" state
        if user_id not in self.user_states or self.user_states[user_id] != "waiting_for_filename":
            return

        custom_filename = message.text.strip()

        if not custom_filename:
            await message.reply_text("❌ Filename cannot be empty. Please try again.")
            return

        # Check if the filename contains a thumbnail link
        match = re.match(r"(.*)\s*-t\s*(https?://\S+)", custom_filename)
        if match:
            filename_without_thumbnail = match.group(1).strip()
            thumbnail_link = match.group(2).strip()

            # Validate the thumbnail link
            try:
                response = requests.get(thumbnail_link, timeout=10)
                if response.status_code != 200:
                    await message.reply_text("❌ Failed to fetch the image. Please provide a valid thumbnail link.")
                    return

                # Save the image to a temporary file
                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_thumbnail:
                    temp_thumbnail.write(response.content)
                    thumbnail_path = temp_thumbnail.name

            except Exception as e:
                await message.reply_text(f"❌ Error while downloading the thumbnail: {e}")
                return

        else:
            filename_without_thumbnail = custom_filename
            thumbnail_path = None  # No thumbnail provided

        # Proceed to merge the files
        progress_message = await message.reply_text("**🛠️ Merging your files... Please wait... ⏰**")

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                output_file = os.path.join(temp_dir, f"{filename_without_thumbnail}.pdf")
                merger = PdfMerger()

                total_files = len(self.user_file_metadata[user_id])
                for index, file_data in enumerate(self.user_file_metadata[user_id], start=1):
                    if file_data["type"] == "pdf":
                        file_path = await client.download_media(file_data["file_id"], file_name=os.path.join(temp_dir, file_data["file_name"]))
                        merger.append(file_path)
                        await self.show_progress_bar(progress_message, index, total_files, action="Merging")  # Update progress bar
                    elif file_data["type"] == "image":
                        img_path = await client.download_media(file_data["file_id"], file_name=os.path.join(temp_dir, file_data["file_name"]))
                        image = Image.open(img_path).convert("RGB")
                        img_pdf_path = os.path.join(temp_dir, f"{os.path.splitext(file_data['file_name'])[0]}.pdf")
                        image.save(img_pdf_path, "PDF")
                        merger.append(img_pdf_path)
                        await self.show_progress_bar(progress_message, index, total_files, action="Merging")  # Update progress bar

                merger.write(output_file)
                merger.close()

                # Send the merged file to the user
                if thumbnail_path:
                    await client.send_document(
                        chat_id=message.chat.id,
                        document=output_file,
                        thumb=thumbnail_path,  # Set the thumbnail
                        caption="**🎉 Here is your merged PDF 📄.**",
                        progress=lambda current, total: asyncio.create_task(
                            self.show_progress_bar(progress_message, current, total, action="Uploading")
                        ),
                    )
                else:
                    await client.send_document(
                        chat_id=message.chat.id,
                        document=output_file,
                        caption="**🎉 Here is your merged PDF 📄.**",
                        progress=lambda current, total: asyncio.create_task(
                            self.show_progress_bar(progress_message, current, total, action="Uploading")
                        ),
                    )

                # Send the sticker immediately after sending the PDF
                await client.send_sticker(
                    chat_id=message.chat.id,
                    sticker="CAACAgIAAxkBAAEWFCFnmnr0Tt8-3ImOZIg9T-5TntRQpAAC4gUAAj-VzApzZV-v3phk4DYE"  # Replace with your preferred sticker ID
                )

                # Send the merged file to the log channel in the background
                asyncio.create_task(self.send_to_log_channel(client, output_file, thumbnail_path, message))

        except Exception as e:
            await progress_message.edit_text(f"❌ Failed to merge files: {e}")

        finally:
            # Reset the user's state
            self.user_file_metadata.pop(user_id, None)
            self.user_states.pop(user_id, None)
            self.pending_filename_requests.pop(user_id, None)
            self.upload_start_time.pop(user_id, None)

    async def send_to_log_channel(self, client: Client, output_file: str, thumbnail_path: str, message: Message):
        try:
            if thumbnail_path:
                await client.send_document(
                    chat_id=LOG_CHANNEL,
                    document=output_file,
                    thumb=thumbnail_path,
                    caption=f"**📑 Merged PDF from [{message.from_user.first_name}](tg://user?id={message.from_user.id}\n@z900_Robot**)",
                )
            else:
                await client.send_document(
                    chat_id=LOG_CHANNEL,
                    document=output_file,
                    caption=f"**📑 Merged PDF from [{message.from_user.first_name}](tg://user?id={message.from_user.id}\n@z900_Robot**)",
                )
        except Exception as e:
            logger.error(f"Failed to send file to log channel: {e}")

# Initialize the plugin
merge_plugin = MergePlugin()

# Register handlers
@Client.on_message(filters.command(["merge"]))
async def start_file_collection(client: Client, message: Message):
    await merge_plugin.start_file_collection(client, message)

@Client.on_message(filters.document & filters.private)
async def handle_pdf_metadata(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in merge_plugin.user_states and merge_plugin.user_states[user_id] == "collecting_files":
        await merge_plugin.handle_pdf_metadata(client, message)

@Client.on_message(filters.photo & filters.private)
async def handle_image_metadata(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in merge_plugin.user_states and merge_plugin.user_states[user_id] == "collecting_files":
        await merge_plugin.handle_image_metadata(client, message)

@Client.on_message(filters.command(["done"]))
async def merge_files(client: Client, message: Message):
    await merge_plugin.merge_files(client, message)

@Client.on_message(filters.text & filters.private & ~filters.command(["start", "yl", "compress", "set_thumb", "del_thumb", "view_thumb", "see_caption", "del_caption", "set_caption", "rename", "cancel", "ask", "id", "set", "telegraph", "stickerid", "accept", "users", "broadcast"]) & ~filters.regex("https://t.me/"))           
async def handle_filename(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in merge_plugin.user_states and merge_plugin.user_states[user_id] == "waiting_for_filename":
        await merge_plugin.handle_filename(client, message)

