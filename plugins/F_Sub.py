
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import UserNotParticipant

# Custom filter to check if the user is subscribed
async def not_subscribed(_, client, message):
    if not client.force_channel:
        return False  # Skip check if no force channel is set
    
    try:
        user = await client.get_chat_member(client.force_channel, message.from_user.id)
        if user.status == enums.ChatMemberStatus.BANNED:
            return True  # Treat banned users as not subscribed
        return False  # User is subscribed
    except UserNotParticipant:
        return True  # User is not subscribed
    except Exception as e:
        print(f"Error checking subscription: {e}")
        return False  # Skip check on error

# Handler for non-subscribed users
@Client.on_message(filters.private & filters.create(not_subscribed))
async def is_not_subscribed(client, message):
    # Customizable message and button text
    join_message = "**𝚂𝙾𝚁𝚁𝚈 𝙳𝚄𝙳𝙴 𝚈𝙾𝚄've 𝙽𝙾𝚃 𝙹𝙾𝙸𝙽𝙳 𝙼𝚈 𝙲𝙷𝙰𝙽𝙽𝙴𝙻 😔. 𝙿𝙻𝙴𝙰𝚂𝙴 𝙹𝙾𝙸𝙽 𝙼𝚈 𝙲𝙷𝙰𝙽𝙽𝙴𝙻 𝚃𝙾 𝚄𝚂𝙴 𝚃𝙷𝙸𝚂 𝙱𝙾𝚃. 🙏 "

    join_button_text = "📢 𝙹𝚘𝚒𝚗 𝙼𝚢 𝚄𝚙𝚍𝚊𝚝𝚎 𝙲𝚑𝚊𝚗𝚗𝚎𝚕 📢"
    check_again_button_text = "🔄 Check Again 🔄"
    
    # Buttons
    buttons = [
        [InlineKeyboardButton(text=join_button_text, url=client.invitelink)],
        [InlineKeyboardButton(text=check_again_button_text, callback_data="check_subscription")]
    ]
    
    # Send the message
    await message.reply_text(
        text=join_message,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_callback_query(filters.regex("check_subscription"))
async def check_subscription_callback(client, callback_query):
    user_id = callback_query.from_user.id
    
    try:
        user = await client.get_chat_member(client.force_channel, user_id)
        if user.status != enums.ChatMemberStatus.BANNED:
            # User is subscribed - trigger /start command
            await client.send_message(user_id, "/start")  # Trigger /start command
            return
    except UserNotParticipant:
        pass  # User is still not subscribed
    
    # User is not subscribed - prompt them to join
    await callback_query.answer("**𝚂𝙾𝚁𝚁𝚈 𝙳𝚄𝙳𝙴 𝚈𝙾𝚄've 𝙽𝙾𝚃 𝙹𝙾𝙸𝙽𝙳 𝙼𝚈 𝙲𝙷𝙰𝙽𝙽𝙴𝙻 😔. 𝙿𝙻𝙴𝙰𝚂𝙴 𝙹𝙾𝙸𝙽 𝙼𝚈 𝙲𝙷𝙰𝙽𝙽𝙴𝙻 𝚃𝙾 𝚄𝚂𝙴 𝚃𝙷𝙸𝚂 𝙱𝙾𝚃. 🙏 **", show_alert=True)
