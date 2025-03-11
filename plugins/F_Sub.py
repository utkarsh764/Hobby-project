# force_subscribe.py

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from config import *

async def is_subscribed(filter, client, update, channel_id):
    if not channel_id:
        return True
    user_id = update.from_user.id
    if user_id in ADMIN:
        return True
    try:
        member = await client.get_chat_member(chat_id=channel_id, user_id=user_id)
    except UserNotParticipant:
        return False

    if not member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.MEMBER]:
        return False
    else:
        return True

async def is_subscribed1(filter, client, update):
    return await is_subscribed(filter, client, update, FORCE_SUB_CHANNEL1)

async def is_subscribed2(filter, client, update):
    return await is_subscribed(filter, client, update, FORCE_SUB_CHANNEL2)

async def is_subscribed3(filter, client, update):
    return await is_subscribed(filter, client, update, FORCE_SUB_CHANNEL3)

async def is_subscribed4(filter, client, update):
    return await is_subscribed(filter, client, update, FORCE_SUB_CHANNEL4)

subscribed1 = filters.create(is_subscribed1)
subscribed2 = filters.create(is_subscribed2)
subscribed3 = filters.create(is_subscribed3)
subscribed4 = filters.create(is_subscribed4)
