import sys
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from config import (
    F_SUB_1, F_SUB_2, F_SUB_3, F_SUB_4,  # Replace FORCE_SUB_CHANNEL1, FORCE_SUB_CHANNEL2, etc.
    FORCE_PIC, FORCE_MSG, CHANNEL_ID
)

# Initialize the bot
app = Client("my_bot")

async def start_bot():
    await app.start()
    usr_bot_me = await app.get_me()
    app.uptime = datetime.now()

    # Fetch invite links for force-subscribe channels
    if F_SUB_1:
        try:
            link = (await app.get_chat(F_SUB_1)).invite_link
            if not link:
                await app.export_chat_invite_link(F_SUB_1)
                link = (await app.get_chat(F_SUB_1)).invite_link
            app.invitelink1 = link
        except Exception as a:
            app.LOGGER(__name__).warning(a)
            app.LOGGER(__name__).warning("Bot can't Export Invite link from Force Sub Channel!")
            app.LOGGER(__name__).warning(f"Please Double check the F_SUB_1 value and Make sure Bot is Admin in channel with Invite Users via Link Permission, Current Force Sub Channel Value: {F_SUB_1}")
            app.LOGGER(__name__).info("\nBot Stopped. https://t.me/weebs_support for support")
            sys.exit()

    if F_SUB_2:
        try:
            link = (await app.get_chat(F_SUB_2)).invite_link
            if not link:
                await app.export_chat_invite_link(F_SUB_2)
                link = (await app.get_chat(F_SUB_2)).invite_link
            app.invitelink2 = link
        except Exception as a:
            app.LOGGER(__name__).warning(a)
            app.LOGGER(__name__).warning("Bot can't Export Invite link from Force Sub Channel!")
            app.LOGGER(__name__).warning(f"Please Double check the F_SUB_2 value and Make sure Bot is Admin in channel with Invite Users via Link Permission, Current Force Sub Channel Value: {F_SUB_2}")
            app.LOGGER(__name__).info("\nBot Stopped. https://t.me/weebs_support for support")
            sys.exit()

    if F_SUB_3:
        try:
            link = (await app.get_chat(F_SUB_3)).invite_link
            if not link:
                await app.export_chat_invite_link(F_SUB_3)
                link = (await app.get_chat(F_SUB_3)).invite_link
            app.invitelink3 = link
        except Exception as a:
            app.LOGGER(__name__).warning(a)
            app.LOGGER(__name__).warning("Bot can't Export Invite link from Force Sub Channel!")
            app.LOGGER(__name__).warning(f"Please Double check the F_SUB_3 value and Make sure Bot is Admin in channel with Invite Users via Link Permission, Current Force Sub Channel Value: {F_SUB_3}")
            app.LOGGER(__name__).info("\nBot Stopped. https://t.me/weebs_support for support")
            sys.exit()

    if F_SUB_4:
        try:
            link = (await app.get_chat(F_SUB_4)).invite_link
            if not link:
                await app.export_chat_invite_link(F_SUB_4)
                link = (await app.get_chat(F_SUB_4)).invite_link
            app.invitelink4 = link
        except Exception as a:
            app.LOGGER(__name__).warning(a)
            app.LOGGER(__name__).warning("Bot can't Export Invite link from Force Sub Channel!")
            app.LOGGER(__name__).warning(f"Please Double check the F_SUB_4 value and Make sure Bot is Admin in channel with Invite Users via Link Permission, Current Force Sub Channel Value: {F_SUB_4}")
            app.LOGGER(__name__).info("\nBot Stopped. https://t.me/weebs_support for support")
            sys.exit()

    # Check if the bot is admin in the database channel
    try:
        db_channel = await app.get_chat(CHANNEL_ID)
        app.db_channel = db_channel
        test = await app.send_message(chat_id=db_channel.id, text="Test Message")
        await test.delete()
    except Exception as e:
        app.LOGGER(__name__).warning(e)
        app.LOGGER(__name__).warning(f"Make Sure bot is Admin in DB Channel, and Double check the CHANNEL_ID Value, Current Value {CHANNEL_ID}")
        app.LOGGER(__name__).info("\nBot Stopped. Join https://t.me/weebs_support for support")
        sys.exit()

    app.set_parse_mode(ParseMode.HTML)
    app.LOGGER(__name__).info(f"Bot Running..!\n\nCreated by \nhttps://t.me/weebs_support")
    app.LOGGER(__name__).info(f"""\n
        ░██████╗░█████╗░██████╗░██╗░░░██╗
        ██╔════╝██╔══██╗██╔══██╗██║░░░██║
        ╚█████╗░██║░░██║██████╔╝██║░░░██║
        ░╚═══██╗██║░░██║██╔══██╗██║░░░██║
        ██████╔╝╚█████╔╝██║░░██║╚██████╔╝
        ╚═════╝░░╚════╝░╚═╝░░╚═╝░╚═════╝░
        """)

@app.on_message(filters.command('start') & filters.private)
async def not_joined(client: Client, message: Message):
    # Initialize buttons list
    buttons = []

    # Check if the first and second channels are both set
    if F_SUB_1 and F_SUB_2:
        buttons.append([
            InlineKeyboardButton(text="• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ •", url=client.invitelink1),
            InlineKeyboardButton(text="• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ •", url=client.invitelink2),
        ])
    # Check if only the first channel is set
    elif F_SUB_1:
        buttons.append([
            InlineKeyboardButton(text="• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ •", url=client.invitelink1)
        ])
    # Check if only the second channel is set
    elif F_SUB_2:
        buttons.append([
            InlineKeyboardButton(text="• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ •", url=client.invitelink2)
        ])

    # Check if the third and fourth channels are set
    if F_SUB_3 and F_SUB_4:
        buttons.append([
            InlineKeyboardButton(text="• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ •", url=client.invitelink3),
            InlineKeyboardButton(text="• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ •", url=client.invitelink4),
        ])
    # Check if only the third channel is set
    elif F_SUB_3:
        buttons.append([
            InlineKeyboardButton(text="• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ •", url=client.invitelink3)
        ])
    # Check if only the fourth channel is set
    elif F_SUB_4:
        buttons.append([
            InlineKeyboardButton(text="• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ •", url=client.invitelink4)
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

    # Send the message with the photo and buttons
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

# Run the bot
if __name__ == "__main__":
    app.run(start_bot())
