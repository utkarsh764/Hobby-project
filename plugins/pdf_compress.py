import os
import logging
import tempfile
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pikepdf import Pdf, PdfImageCompression
from config import LOG_CHANNEL

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

class CompressPlugin:
    def __init__(self):
        self.user_states = {}  # Track user states

    async def reset_user_state(self, user_id: int):
        await asyncio.sleep(120)  # 2 minutes
        if user_id in self.user_states:
            self.user_states.pop(user_id, None)
            logger.info(f"Reset state for user {user_id} due to inactivity.")

    async def show_progress(self, progress_message: Message, current: int, total: int, action: str):
        """Show download/upload progress."""
        percentage = (current / total) * 100
        progress_bar = "●" * int(percentage / 10) + "○" * (10 - int(percentage / 10))
        text = f"**🛠️ {action.capitalize()}...**\n`[{progress_bar}]` {percentage:.1f}% ({current}/{total} bytes)"
        await progress_message.edit_text(text)

    async def compress_pdf(self, input_path: str, output_path: str, compression_level: str):
        """Compress a PDF using pikepdf."""
        compression_map = {
            "low": PdfImageCompression.jpeg_low,
            "medium": PdfImageCompression.jpeg_medium,
            "high": PdfImageCompression.jpeg_high,
        }
        with Pdf.open(input_path) as pdf:
            pdf.save(output_path, compress_streams=True, compression_level=compression_map[compression_level])
        logger.info(f"Compressed PDF saved to {output_path} with {compression_level} compression")

    async def estimate_compressed_size(self, input_path: str, compression_level: str) -> int:
        """Estimate the size of the compressed PDF."""
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
            await self.compress_pdf(input_path, temp_path, compression_level)
            compressed_size = os.path.getsize(temp_path)
            os.remove(temp_path)
        return compressed_size

    async def send_compression_options(self, client: Client, message: Message, file_path: str):
        """Send a message with compression options and estimated sizes."""
        # Estimate sizes for low, medium, and high compression
        low_size = await self.estimate_compressed_size(file_path, "low")
        medium_size = await self.estimate_compressed_size(file_path, "medium")
        high_size = await self.estimate_compressed_size(file_path, "high")

        # Create buttons for compression options
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(f"Low (~{low_size // 1024} KB)", callback_data="compress_low")],
                [InlineKeyboardButton(f"Medium (~{medium_size // 1024} KB)", callback_data="compress_medium")],
                [InlineKeyboardButton(f"High (~{high_size // 1024} KB)", callback_data="compress_high")],
            ]
        )

        # Send the message with compression options
        await message.reply_text(
            "**🛠️ Choose a compression level:**\n"
            f"Low: ~{low_size // 1024} KB\n"
            f"Medium: ~{medium_size // 1024} KB\n"
            f"High: ~{high_size // 1024} KB",
            reply_markup=keyboard,
        )

    async def handle_compress_command(self, client: Client, message: Message):
        """Handle the /compress command when it's a reply to a PDF."""
        user_id = message.from_user.id

        # Check if the command is a reply to a message
        if not message.reply_to_message:
            await message.reply_text("❌ Please reply to a PDF message with /compress.")
            return

        # Check if the replied message contains a PDF
        replied_message = message.reply_to_message
        if not replied_message.document or replied_message.document.mime_type != "application/pdf":
            await message.reply_text("❌ The replied message is not a valid PDF. Please reply to a PDF.")
            return

        # Check file size
        if replied_message.document.file_size > MAX_FILE_SIZE:
            await message.reply_text("🚫 File size is too large! Please send a file under 500MB.")
            return

        # Download the PDF
        progress_message = await message.reply_text("**🛠️ Downloading your PDF... Please wait... ⏰**")
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                file_path = await client.download_media(
                    replied_message.document.file_id,
                    file_name=os.path.join(temp_dir, replied_message.document.file_name),
                    progress=lambda current, total: asyncio.create_task(
                        self.show_progress(progress_message, current, total, "downloading")
                    ),
                )
                await progress_message.edit_text("**🛠️ PDF downloaded! Choose a compression level below.**")

                # Send compression options
                await self.send_compression_options(client, message, file_path)

        except Exception as e:
            await progress_message.edit_text(f"❌ Failed to download PDF: {e}")

    async def handle_compression_callback(self, client: Client, callback_query: CallbackQuery):
        """Handle compression level selection."""
        user_id = callback_query.from_user.id
        compression_level = callback_query.data.split("_")[1]  # Extract compression level from callback data

        # Get the original PDF path from the user's state
        if user_id not in self.user_states or "file_path" not in self.user_states[user_id]:
            await callback_query.answer("❌ No PDF found. Please start over.")
            return

        file_path = self.user_states[user_id]["file_path"]
        progress_message = await callback_query.message.reply_text(f"**🛠️ Compressing your PDF ({compression_level} level)... Please wait... ⏰**")

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                compressed_file_path = os.path.join(temp_dir, f"compressed_{os.path.basename(file_path)}")
                await self.compress_pdf(file_path, compressed_file_path, compression_level)

                # Send the compressed PDF back to the user
                await client.send_document(
                    chat_id=callback_query.message.chat.id,
                    document=compressed_file_path,
                    caption=f"**🎉 Here is your compressed PDF ({compression_level} level)!**",
                    progress=lambda current, total: asyncio.create_task(
                        self.show_progress(progress_message, current, total, "uploading")
                    ),
                )

                # Send the compressed PDF to the log channel in the background
                asyncio.create_task(self.send_to_log_channel(client, compressed_file_path, callback_query.message))

        except Exception as e:
            await progress_message.edit_text(f"❌ Failed to compress PDF: {e}")
        finally:
            # Reset the user's state
            self.user_states.pop(user_id, None)

    async def send_to_log_channel(self, client: Client, file_path: str, message: Message):
        """Send the compressed PDF to the log channel."""
        try:
            await client.send_document(
                chat_id=LOG_CHANNEL,
                document=file_path,
                caption=f"**📑 Compressed PDF from [{message.from_user.first_name}](tg://user?id={message.from_user.id})**"
            )
        except Exception as e:
            logger.error(f"Failed to send file to log channel: {e}")

# Initialize the plugin
compress_plugin = CompressPlugin()

# Register handlers
@Client.on_message(filters.command(["compress"]))
async def handle_compress_command(client: Client, message: Message):
    await compress_plugin.handle_compress_command(client, message)

@Client.on_callback_query(filters.regex(r"^compress_(low|medium|high)$"))
async def handle_compression_callback(client: Client, callback_query: CallbackQuery):
    await compress_plugin.handle_compression_callback(client, callback_query

                                                      
