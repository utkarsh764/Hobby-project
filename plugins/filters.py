from pyrogram import filters

# Custom filter to allow only user messages (not from bots)
def user_only(_, __, message):
    return not message.from_user.is_bot if message.from_user else False

user_filter = filters.create(user_only)
