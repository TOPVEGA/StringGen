import logging
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup

from StringGen.generate import (
    generate_session,
    ASK_QUES,
    BUTTONS_QUES,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ERROR_MESSAGE = (
    "حدث خطأ أثناء توليد الجلسة:\n\n"
    "• تأكد من اتصال الإنترنت لديك.\n"
    "• تحقق من صحة الـ API ورقم الهاتف أو توكن البوت.\n"
    "• إذا استمرت المشكلة، راسل المطور @g9uuu"
)

CALLBACK_PATTERN = r"^(generate|pyrogram_v1|pyrogram_v2|pyrogram_bot|telethon|telethon_bot)$"

@Client.on_callback_query(filters.regex(CALLBACK_PATTERN))
async def sessiongen_callbacks(bot: Client, cq: CallbackQuery):
    choice = cq.data
    try:
        await cq.answer()

        if choice == "generate":
            return await cq.message.reply(
                ASK_QUES,
                reply_markup=InlineKeyboardMarkup(BUTTONS_QUES)
            )

        if choice == "pyrogram_v1":
            return await generate_session(bot, cq.message, old_pyro=True)

        if choice == "pyrogram_v2":
            return await generate_session(bot, cq.message)

        if choice == "pyrogram_bot":
            await cq.answer("» جاري توليد جلسة بايروجرام بوت...", show_alert=True)
            return await generate_session(bot, cq.message, is_bot=True)

        if choice == "telethon":
            return await generate_session(bot, cq.message, telethon=True)

        if choice == "telethon_bot":
            return await generate_session(bot, cq.message, telethon=True, is_bot=True)

        await cq.message.reply("⚠️ حدث خطأ غير متوقع")

    except Exception:
        logger.exception("⚠️ خطأ في معالجة الاستجابة")
        await cq.message.reply(ERROR_MESSAGE, disable_web_page_preview=True)