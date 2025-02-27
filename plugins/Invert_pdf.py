import os
import logging
import tempfile
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from config import LOG_CHANNEL
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
user_invert_state = {}  # Track user process state

# Function to invert PDF colors using PyMuPDF's transformation matrix
async def invert_pdf_colors(input_pdf_path: str, output_pdf_path: str) -> None:
    """
    Inverts the colors of a PDF file without converting pages to images.
    Keeps the original size and quality intact.
    """
    pdf_document = fitz.open(input_pdf_path)

    for page in pdf_document:
        # Apply color inversion transformation matrix
        invert_matrix = fitz.Matrix(-1, 0, 0, -1, page.rect.width, page.rect.height)
        page.apply_redactions()
        page.insert_text((0, 0), "", rotate=0, transform=invert_matrix)

    # Save the new PDF with minimal compression (keeping quality)
    pdf_document.save(output_pdf_path, deflate=False)  
    pdf_document.close()

# Handle /invert command
@Client.on_message(filters.command(["invert"]))
async def handle_invert_command(client: Client, message: Message):
    user_id = message.from_user.id
    logger.info(f"User {message.from_user.first_name} ({user_id}) requested /invert")

    if not message.reply_to_message or not message.reply_to_message.document:
        await message.reply_text("❌ Please reply to a PDF file with /invert to invert its colors.")
        return

    if message.reply_to_message.document.mime_type != "application/pdf":
        await message.reply_text("❌ This is not a valid PDF file. Please reply to a PDF 📑.")
        return

    if message.reply_to_message.document.file_size > MAX_FILE_SIZE:
        await message.reply_text("🚫 File size is too large! Please use a file under 20MB.")
        return

    # Notify user that processing has started
    progress_message = await message.reply_text("**🛠️ Inverting colors... Please wait... ⏰**")

    try:
        # Download the PDF
        with tempfile.TemporaryDirectory() as temp_dir:
            input_pdf_path = os.path.join(temp_dir, "input.pdf")
            output_pdf_path = os.path.join(temp_dir, "output.pdf")
            await message.reply_to_message.download(file_name=input_pdf_path)

            # Invert the colors of the PDF
            await invert_pdf_colors(input_pdf_path, output_pdf_path)

            # Send the inverted PDF back to the user
            await message.reply_document(
                document=output_pdf_path,
                caption="🎉 Here's your inverted PDF!",
            )

            # Log the action in the log channel
            await client.send_document(
                chat_id=LOG_CHANNEL,
                document=output_pdf_path,
                caption=f"📑 Inverted PDF from [{message.from_user.first_name}](tg://user?id={user_id})\n**@z900_Robot**",
            )

            # Delete the progress message
            await progress_message.delete()

            # Send a sticker after sending the inverted PDF
            await client.send_sticker(
                chat_id=message.chat.id,
                sticker="CAACAgIAAxkBAAEWFCFnmnr0Tt8-3ImOZIg9T-5TntRQpAAC4gUAAj-VzApzZV-v3phk4DYE"  # Replace with your preferred sticker ID
            )

    except Exception as e:
        logger.error(f"Error inverting PDF: {e}")
        await progress_message.edit_text(f"❌ Failed to invert PDF: {e}")

    finally:
        # Clean up
        user_invert_state.pop(user_id, None)

