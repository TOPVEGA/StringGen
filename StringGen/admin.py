import tempfile
from datetime import timedelta, timezone
from pyrogram import Client, filters
from pyrogram.types import Message
from config import OWNER_ID
from StringGen.database import users

IST = timezone(timedelta(hours=5, minutes=30))

@Client.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def stats_handler(_, message: Message):
    total = await users.count_documents({})
    await message.reply_text(f"📊 **ᴛᴏᴛᴀʟ ᴜꜱᴇʀꜱ:** `{total}`")


@Client.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_handler(bot: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❗ **ᴜꜱᴀɢᴇ:** `/broadcast your message here`")

    text = message.text.split(None, 1)[1]
    success, failed = 0, 0

    async for user in users.find({}, {"_id": 1}):
        try:
            await bot.send_message(user["_id"], text)
            success += 1
        except Exception:
            failed += 1

    await message.reply_text(
        f"✅ **ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ.**\n\n"
        f"📬 **ᴅᴇʟɪᴠᴇʀᴇᴅ:** `{success}`\n"
        f"⚠️ **ꜰᴀɪʟᴇᴅ:** `{failed}`"
    )


@Client.on_message(filters.command("users") & filters.user(OWNER_ID))
async def users_list(bot: Client, message: Message):
    lines = []
    count = 0

    async for user in users.find().sort("joined", -1):
        uid = user["_id"]
        name = user.get("name", "N/A")
        username = user.get("username", "N/A")
        joined = user.get("joined")
        if joined:
            join_time = joined.astimezone(IST)
            join_info = join_time.strftime('%d-%m-%Y %I:%M %p') + " IST"
        else:
            join_info = "Unknown"

        lines.append(f"{uid} • {name} (@{username}) — Joined: {join_info}")
        count += 1

    total = await users.count_documents({})

    if count <= 50:
        reply_text = "**👥 ʀᴇɢɪꜱᴛᴇʀᴇᴅ ᴜꜱᴇʀꜱ:**\n\n"
        reply_text += "\n".join([f"• `{line}`" for line in lines])
        reply_text += f"\n\n➕ **ᴛᴏᴛᴀʟ:** `{total}`"
        await message.reply_text(reply_text)
    else:
        with tempfile.NamedTemporaryFile("w+", encoding="utf-8", suffix=".txt") as file:
            file.write("\n".join(lines))
            file.seek(0)
            await message.reply_document(
                file.name,
                caption=f"👥 ᴛᴏᴛᴀʟ ᴜꜱᴇʀꜱ: `{total}`"
            )
