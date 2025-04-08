# Written By [MaskedVirus | swatv3nub] for William and Ryūga
# Kang With Proper Credits

from pyrogram import filters

from wbb import app
from wbb.core.decorators.permissions import adminsOnly
from wbb.utils.dbfunctions import (
    antiservice_off,
    antiservice_on,
    is_antiservice_on,
)

__MODULE__ = "AntiService"
__HELP__ = """
Plugin xóa tin nhắn dịch vụ trong cuộc trò chuyện!

/antiservice [enable|disable]
"""


@app.on_message(filters.command("antiservice") & ~filters.private)
@adminsOnly("can_change_info")
async def anti_service(_, message):
    if len(message.command) != 2:
        return await message.reply_text(
            "Cách sử dụng: /antiservice [enable | disable]"
        )
    status = message.text.split(None, 1)[1].strip()
    status = status.lower()
    chat_id = message.chat.id
    if status == "enable":
        await antiservice_on(chat_id)
        await message.reply_text(
            "Đã bật Hệ thống AntiService. Tôi sẽ xóa tin nhắn dịch vụ từ bây giờ."
        )
    elif status == "disable":
        await antiservice_off(chat_id)
        await message.reply_text(
            "Đã vô hiệu hóa Hệ thống AntiService. Tôi sẽ không xóa tin nhắn dịch vụ từ bây giờ."
        )
    else:
        await message.reply_text(
            "Lệnh không đúng, Dùng /antiservice [enable|disable]"
        )


@app.on_message(filters.service, group=11)
async def delete_service(_, message):
    chat_id = message.chat.id
    try:
        if await is_antiservice_on(chat_id):
            return await message.delete()
    except Exception:
        pass
