# force_sub.py

from pyrogram import Client, filters
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
#=====================================================================================
#force sub reply (don't touch it)

async def force_sub_message(client: Client, message: Message):
    # Initialize buttons list
    buttons = []

    # Check if the first and second channels are both set
    if FORCE_SUB_CHANNEL1 and FORCE_SUB_CHANNEL2:
        buttons.append([
            InlineKeyboardButton(text="• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=client.invitelink1),
            InlineKeyboardButton(text="ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ •", url=client.invitelink2),
        ])
    # Check if only the first channel is set
    elif FORCE_SUB_CHANNEL1:
        buttons.append([
            InlineKeyboardButton(text="• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ•", url=client.invitelink1)
        ])
    # Check if only the second channel is set
    elif FORCE_SUB_CHANNEL2:
        buttons.append([
            InlineKeyboardButton(text="• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ•", url=client.invitelink2)
        ])

    # Check if the third and fourth channels are set
    if FORCE_SUB_CHANNEL3 and FORCE_SUB_CHANNEL4:
        buttons.append([
            InlineKeyboardButton(text="• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", url=client.invitelink3),
            InlineKeyboardButton(text="ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ •", url=client.invitelink4),
        ])
    # Check if only the first channel is set
    elif FORCE_SUB_CHANNEL3:
        buttons.append([
            InlineKeyboardButton(text="• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ•", url=client.invitelink3)
        ])
    # Check if only the second channel is set
    elif FORCE_SUB_CHANNEL4:
        buttons.append([
            InlineKeyboardButton(text="• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ•", url=client.invitelink4)
        ])

    # Append "Try Again" button if the command has a second argument
    try:
        buttons.append([
            InlineKeyboardButton(
                text="ʀᴇʟᴏᴀᴅ",
                url=f"https://t.me/{client.username}?start={message.command[1]}"
            )
        ])
    except IndexError:
        pass  # Ignore if no second argument is present

    await message.reply_photo(
        photo=FORCE_PIC,
        caption=FORCE_MSG.format(
        first=message.from_user.first_name,
        last=message.from_user.last_name,
        username=None if not message.from_user.username else '@' + message.from_user.username,
        mention=message.from_user.mention,
        id=message.from_user.id
    ),
    reply_markup=InlineKeyboardMarkup(buttons)#,
    #message_effect_id=5104841245755180586  # Add the effect ID here
    )

#=====================================================================================

# Filters for Subscription Checks
subscribed1 = filters.create(lambda _, __, ___: check_subscription(_, __.from_user.id))
subscribed2 = filters.create(lambda _, __, ___: check_subscription(_, __.from_user.id))
subscribed3 = filters.create(lambda _, __, ___: check_subscription(_, __.from_user.id))
subscribed4 = filters.create(lambda _, __, ___: check_subscription(_, __.from_user.id))

