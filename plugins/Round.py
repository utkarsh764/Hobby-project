import os
from pyrogram import Client, filters
from pyrogram.types import Message
from moviepy.editor import VideoFileClip
from moviepy.video.fx.all import crop

# Helper function to create a video note (circular video)
def create_video_note(input_video_path, output_video_path):
    # Load the video
    clip = VideoFileClip(input_video_path)

    # Get the dimensions of the video
    width, height = clip.size

    # Determine the size of the square (smallest dimension)
    min_dimension = min(width, height)

    # Crop the video to a square
    clip = crop(clip, width=min_dimension, height=min_dimension, x_center=width // 2, y_center=height // 2)

    # Resize the video to 512x512 (Telegram's video note size)
    clip = clip.resize((512, 512))

    # Write the output video
    clip.write_videofile(output_video_path, codec="libx264", audio_codec="aac")

# Pyrogram bot handler
@Client.on_message(filters.command("round") & filters.reply)
async def round_video_command(client: Client, message: Message):
    try:
        # Check if the replied message contains a video
        if not message.reply_to_message.video:
            await message.reply("❌ Please reply to a video file with /round.")
            return

        # Download the video file
        video = message.reply_to_message.video
        file_path = await message.reply_to_message.download()

        # Create output file path
        output_path = f"video_note_{video.file_name}"

        # Convert the video to a video note
        create_video_note(file_path, output_path)

        # Send the video note back to the user
        await message.reply_video_note(
            video_note=output_path,
            caption="🎥 Here's your video note!"
        )

        # Clean up temporary files
        os.remove(file_path)
        os.remove(output_path)

    except Exception as e:
        await message.reply(f"❌ An error occurred: {e}")
