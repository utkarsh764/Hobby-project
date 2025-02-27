import os
import numpy as np
from pydub import AudioSegment
from pydub.playback import play
from pyrogram import Client, filters
from pyrogram.types import Message

# Helper function to create 8D audio effect
def create_8d_effect(input_audio_path, output_audio_path):
    # Load the audio file
    audio = AudioSegment.from_file(input_audio_path)

    # Convert audio to numpy array for manipulation
    samples = np.array(audio.get_array_of_samples())
    sample_rate = audio.frame_rate

    # Create a panning effect
    length = len(samples)
    pan = np.sin(2 * np.pi * np.arange(length) / (sample_rate * 0.5))  # Panning frequency
    pan = (pan + 1) / 2  # Normalize to 0-1 range

    # Apply panning to left and right channels
    left_channel = samples * (1 - pan)
    right_channel = samples * pan

    # Combine channels into stereo
    stereo_samples = np.column_stack((left_channel, right_channel)).flatten()

    # Convert back to AudioSegment
    stereo_audio = AudioSegment(
        stereo_samples.tobytes(),
        frame_rate=sample_rate,
        sample_width=audio.sample_width,
        channels=2
    )

    # Export the 8D audio
    stereo_audio.export(output_audio_path, format="mp3")

# Pyrogram bot handler
@Client.on_message(filters.command("8d") & filters.reply)
async def eight_d_command(client: Client, message: Message):
    try:
        # Check if the replied message contains audio
        if not message.reply_to_message.audio:
            await message.reply("❌ Please reply to an audio file with /8d.")
            return

        # Download the audio file
        audio = message.reply_to_message.audio
        file_path = await message.reply_to_message.download()

        # Create output file path
        output_path = f"8d_{audio.file_name}"

        # Apply 8D effect
        create_8d_effect(file_path, output_path)

        # Send the 8D audio back to the user
        await message.reply_audio(
            audio=output_path,
            caption="🎧 Here's your 8D audio!"
        )

        # Clean up temporary files
        os.remove(file_path)
        os.remove(output_path)

    except Exception as e:
        await message.reply(f"❌ An error occurred: {e}")
