import logging
from typing import Union
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import UserNotParticipant, ChatAdminRequired, ChatWriteForbidden
from config import OWNER_ID
from StringGen.save_user import save_user
from StringGen.database import users
from StringGen.database import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def command_filter(cmd: Union[str, list]) -> filters.Filter:
    return filters.private & filters.incoming & filters.command(cmd)

@Client.on_message(command_filter(["start", "help"]))
async def start_handler(bot: Client, message: Message):
    user = message.from_user
    await save_user(user)

    try:
        bot_info = await bot.get_me()
        bot_name = bot_info.first_name or "البوت"

        response_text = (
            f"مرحبًا {user.mention},\n\n"
            f"أنا {bot_name} - بوت متخصص في توليد جلسات التليجرام.\n"
            "يمكنني مساعدتك في إنشاء جلسات بايروجرام أو تيليثون بكل سهولة وأمان\n."
            "صناعه خاصه : @TOPVEGA \n\n"
            "اضغط على الزر أدناه لبدء إنشاء جلسة جديدة"
        )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("إنشاء جلسة جديدة", callback_data="generate")],
            [
                InlineKeyboardButton("مطور", url="https://t.me/g9uuu"),
                
            ]
        ])

        await message.reply_text(
            text=response_text,
            reply_markup=keyboard,
            disable_web_page_preview=True
        )

    except Exception as e:
        logger.exception("حدث خطأ في معالجة أمر /start أو /help:")
        await message.reply_text(
            "حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى لاحقًا."
        )