# shivu/__main__.py
import importlib
import time
import random
import re
import asyncio
from html import escape

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.handlers import MessageHandler

from shivu import (
    collection,
    top_global_groups_collection,
    group_user_totals_collection,
    user_collection,
    user_totals_collection,
    shivu,  # pyrogram Client instance exported from shivu.__init__
    SUPPORT_CHAT,
    UPDATE_CHAT,
    db,
    LOGGER,
)
from shivu.modules import ALL_MODULES


locks = {}
message_counters = {}
spam_counters = {}
last_characters = {}
sent_characters = {}
first_correct_guesses = {}
message_counts = {}

for module_name in ALL_MODULES:
    importlib.import_module("shivu.modules." + module_name)


last_user = {}
warned_users = {}


def escape_markdown(text):
    escape_chars = r'\*_`\\~>#+-=|{}.!'
    return re.sub(r'([%s])' % re.escape(escape_chars), r'\\\1', text)


async def message_counter(client, message) -> None:
    # normalize chat_id to string for dictionary keys (keeps parity with DB keys if stored as string)
    chat_id = str(message.chat.id)
    user = message.from_user
    if not user:
        return

    user_id = user.id

    if chat_id not in locks:
        locks[chat_id] = asyncio.Lock()
    lock = locks[chat_id]

    async with lock:
        chat_frequency = await user_totals_collection.find_one({"chat_id": chat_id})
        if chat_frequency:
            message_frequency = chat_frequency.get("message_frequency", 100)
        else:
            message_frequency = 100

        if chat_id in last_user and last_user[chat_id]["user_id"] == user_id:
            last_user[chat_id]["count"] += 1
            if last_user[chat_id]["count"] >= 10:
                if user_id in warned_users and time.time() - warned_users[user_id] < 600:
                    return
                else:
                    await message.reply_text(
                        f"⚠️ Don't Spam {user.first_name}...\nYour Messages Will be ignored for 10 Minutes..."
                    )
                    warned_users[user_id] = time.time()
                    return
        else:
            last_user[chat_id] = {"user_id": user_id, "count": 1}

        if chat_id in message_counts:
            message_counts[chat_id] += 1
        else:
            message_counts[chat_id] = 1

        if message_counts[chat_id] % message_frequency == 0:
            # send_image expects an Update+Context in original code; adapt to pass client+message
            await send_image(client, message)
            message_counts[chat_id] = 0


async def send_image(client, message) -> None:
    chat_id_int = message.chat.id
    chat_id = str(chat_id_int)

    all_characters = list(await collection.find({}).to_list(length=None))

    if chat_id not in sent_characters:
        sent_characters[chat_id] = []

    if len(sent_characters[chat_id]) == len(all_characters):
        sent_characters[chat_id] = []

    # pick a character whose id not in sent_characters
    available = [c for c in all_characters if c["id"] not in sent_characters[chat_id]]
    if not available:
        # nothing to send
        return

    character = random.choice(available)

    sent_characters[chat_id].append(character["id"])
    last_characters[chat_id] = character

    if chat_id in first_correct_guesses:
        del first_correct_guesses[chat_id]

    await client.send_photo(
        chat_id=chat_id_int,
        photo=character["img_url"],
        caption=f"A New {character['rarity']} Character Appeared...\n/guess Character Name and add in Your Harem",
        parse_mode="Markdown",
    )


async def guess(client, message) -> None:
    chat_id_int = message.chat.id
    chat_id = str(chat_id_int)
    user = message.from_user
    if not user:
        return
    user_id = user.id

    if chat_id not in last_characters:
        return

    if chat_id in first_correct_guesses:
        await message.reply_text("❌️ Already Guessed By Someone.. Try Next Time Bruhh ")
        return

    # get args from message.command (pyrogram provides this)
    args = message.command[1:] if message.command else []
    guess = " ".join(args).lower() if args else ""

    if "()" in guess or "&" in guess.lower():
        await message.reply_text("Nahh You Can't use This Types of words in your guess..❌️")
        return

    name_parts = last_characters[chat_id]["name"].lower().split()

    if sorted(name_parts) == sorted(guess.split()) or any(part == guess for part in name_parts):
        first_correct_guesses[chat_id] = user_id

        user_doc = await user_collection.find_one({"id": user_id})
        if user_doc:
            update_fields = {}
            if getattr(user, "username", None) and user.username != user_doc.get("username"):
                update_fields["username"] = user.username
            if user.first_name != user_doc.get("first_name"):
                update_fields["first_name"] = user.first_name
            if update_fields:
                await user_collection.update_one({"id": user_id}, {"$set": update_fields})

            await user_collection.update_one(
                {"id": user_id}, {"$push": {"characters": last_characters[chat_id]}}
            )

        elif getattr(user, "username", None):
            await user_collection.insert_one(
                {
                    "id": user_id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "characters": [last_characters[chat_id]],
                }
            )

        group_user_total = await group_user_totals_collection.find_one(
            {"user_id": user_id, "group_id": chat_id}
        )
        if group_user_total:
            update_fields = {}
            if getattr(user, "username", None) and user.username != group_user_total.get("username"):
                update_fields["username"] = user.username
            if user.first_name != group_user_total.get("first_name"):
                update_fields["first_name"] = user.first_name
            if update_fields:
                await group_user_totals_collection.update_one(
                    {"user_id": user_id, "group_id": chat_id}, {"$set": update_fields}
                )

            await group_user_totals_collection.update_one(
                {"user_id": user_id, "group_id": chat_id}, {"$inc": {"count": 1}}
            )

        else:
            await group_user_totals_collection.insert_one(
                {
                    "user_id": user_id,
                    "group_id": chat_id,
                    "username": getattr(user, "username", None),
                    "first_name": user.first_name,
                    "count": 1,
                }
            )

        group_info = await top_global_groups_collection.find_one({"group_id": chat_id})
        if group_info:
            update_fields = {}
            if message.chat.title != group_info.get("group_name"):
                update_fields["group_name"] = message.chat.title
            if update_fields:
                await top_global_groups_collection.update_one(
                    {"group_id": chat_id}, {"$set": update_fields}
                )

            await top_global_groups_collection.update_one(
                {"group_id": chat_id}, {"$inc": {"count": 1}}
            )

        else:
            await top_global_groups_collection.insert_one(
                {"group_id": chat_id, "group_name": message.chat.title, "count": 1}
            )

        keyboard = [
            [InlineKeyboardButton(f"See Harem", switch_inline_query_current_chat=f"collection.{user_id}")]
        ]

        await message.reply_text(
            f'<b><a href="tg://user?id={user_id}">{escape(user.first_name)}</a></b> You Guessed a New Character ✅️ \n\n'
            f'𝗡𝗔𝗠𝗘: <b>{last_characters[chat_id]["name"]}</b> \n'
            f'𝗔𝗡𝗜𝗠𝗘: <b>{last_characters[chat_id]["anime"]}</b> \n'
            f'𝗥𝗔𝗜𝗥𝗧𝗬: <b>{last_characters[chat_id]["rarity"]}</b>\n\n'
            "This Character added in Your harem.. use /harem To see your harem",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    else:
        await message.reply_text("Please Write Correct Character Name... ❌️")


async def fav(client, message) -> None:
    user = message.from_user
    if not user:
        return
    user_id = user.id

    args = message.command[1:] if message.command else []
    if not args:
        await message.reply_text("Please provide Character id...")
        return

    character_id = args[0]

    user_doc = await user_collection.find_one({"id": user_id})
    if not user_doc:
        await message.reply_text("You have not Guessed any characters yet....")
        return

    character = next((c for c in user_doc.get("characters", []) if c["id"] == character_id), None)
    if not character:
        await message.reply_text("This Character is Not In your collection")
        return

    user_doc["favorites"] = [character_id]

    await user_collection.update_one({"id": user_id}, {"$set": {"favorites": user_doc["favorites"]}})

    await message.reply_text(f'Character {character["name"]} has been added to your favorite...')


def main() -> None:
    """Register handlers and run the bot."""
    # register command handlers
    shivuu.add_handler(MessageHandler(guess, filters=filters.command(["guess", "protecc", "collect", "grab", "hunt"])))
    shivuu.add_handler(MessageHandler(fav, filters=filters.command(["fav"])))
    # catch-all message counter (runs for all messages)
    shivuu.add_handler(MessageHandler(message_counter, filters=filters.all))

    # Start the client (this blocks)
    LOGGER.info("Starting bot via Pyrogram...")
    shivuu.run()


if __name__ == "__main__":
    LOGGER.info("Bot started")
    main()
