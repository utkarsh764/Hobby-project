from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from helper.utils import not_subscribed

# Handler for users who are not subscribed
@Client.on_message(filters.private & filters.create(not_subscribed))
async def is_not_subscribed(client, message):
    buttons = [
        [InlineKeyboardButton(text="📢 𝙹𝚘𝚒𝚗 𝙼𝚢 𝚞𝚙𝚍𝚊𝚝𝚎𝚜 𝙲𝚑𝚊𝚗𝚗𝚎𝚕 📢", url=client.invitelink)],
        [InlineKeyboardButton(text="🔄 𝚃𝚛𝚢 𝙰𝚐𝚊𝚒𝚗", callback_data="check_subscription")]
    ]
    text = "𝐒𝐨𝐫𝐫𝐲 𝐝𝐮𝐝𝐞 𝐲𝐨𝐮❜𝐯𝐞 𝐧𝐨𝐭 𝐣𝐨𝐢𝐧𝐞𝐝 𝐦𝐲 𝐜𝐡𝐚𝐧𝐧𝐞𝐥 😞. 𝐏𝐥𝐞𝐚𝐬𝐞 𝐣𝐨𝐢𝐧 𝐚𝐧𝐝 𝐜𝐥𝐢𝐜𝐤 𝐨𝐧 𝐭𝐫𝐲 𝐚𝐠𝐚𝐢𝐧. 🔁"
    await message.reply_text(text=text, reply_markup=InlineKeyboardMarkup(buttons))

# Callback query handler for the "Try Again" button
@Client.on_callback_query(filters.regex("check_subscription"))
async def check_subscription(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id

    # Check if the user is subscribed
    if not_subscribed(user_id):  # Assuming not_subscribed can take user_id as an argument
        # If not subscribed, show a popup message
        await callback_query.answer("You are still not subscribed. Please join the channel and click Try again.🔄", show_alert=True)
    else:
        # If subscribed, trigger the start command
        await client.send_message(user_id, "/start")
        await callback_query.answer("Welcome back! You are now subscribed.", show_alert=True)

