# force_sub.py

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from config import *

# Force Check Logic
async def is_subscribed(client, user_id, channel_id):
    """
    Check if a user is subscribed to a specific channel.
    
    Args:
        client: The Pyrogram Client instance.
        user_id: The ID of the user to check.
        channel_id: The ID of the channel to check.
    
    Returns:
        bool: True if the user is subscribed, False otherwise.
    """
    if not channel_id:
        return True
    if user_id in ADMINS:
        return True
    try:
        member = await client.get_chat_member(chat_id=channel_id, user_id=user_id)
        if member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]:
            return True
    except UserNotParticipant:
        return False
    return False

async def check_subscription(client, user_id):
    """
    Check if a user is subscribed to all required channels.
    
    Args:
        client: The Pyrogram Client instance.
        user_id: The ID of the user to check.
    
    Returns:
        bool: True if the user is subscribed to all channels, False otherwise.
    """
    channels = [FORCE_SUB_CHANNEL1, FORCE_SUB_CHANNEL2, FORCE_SUB_CHANNEL3, FORCE_SUB_CHANNEL4]
    for channel_id in channels:
        if channel_id and not await is_subscribed(client, user_id, channel_id):
            return False
    return True

# Force Reply Logic
async def force_sub_message(client: Client, message: Message):
    """
    Send the force subscription message with buttons for each channel.
    """
    buttons = []
    if FORCE_SUB_CHANNEL1:
        buttons.append([InlineKeyboardButton("• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ 1 •", url=client.invitelink1)])
    if FORCE_SUB_CHANNEL2:
        buttons.append([InlineKeyboardButton("• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ 2 •", url=client.invitelink2)])
    if FORCE_SUB_CHANNEL3:
        buttons.append([InlineKeyboardButton("• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ 3 •", url=client.invitelink3)])
    if FORCE_SUB_CHANNEL4:
        buttons.append([InlineKeyboardButton("• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ 4 •", url=client.invitelink4)])

    buttons.append([InlineKeyboardButton("ʀᴇʟᴏᴀᴅ", url=f"https://t.me/{client.username}?start={message.command[1]}")])

    await message.reply_photo(
        photo=FORCE_PIC,
        caption=FORCE_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username=None if not message.from_user.username else '@' + message.from_user.username,
            mention=message.from_user.mention,
            id=message.from_user.id
        ),
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# Filters for Subscription Checks
subscribed1 = filters.create(lambda _, __, ___: check_subscription(_, __.from_user.id))
subscribed2 = filters.create(lambda _, __, ___: check_subscription(_, __.from_user.id))
subscribed3 = filters.create(lambda _, __, ___: check_subscription(_, __.from_user.id))
subscribed4 = filters.create(lambda _, __, ___: check_subscription(_, __.from_user.id))

