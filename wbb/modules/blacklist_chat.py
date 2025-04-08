from pyrogram import filters
from pyrogram.types import Message

from wbb import SUDOERS, app
from wbb.core.decorators.errors import capture_err
from wbb.utils.dbfunctions import (
    blacklist_chat,
    blacklisted_chats,
    whitelist_chat,
)

__MODULE__ = "Blacklist Chat"
__HELP__ = """
**MODULE NÀY CHỈ DÀNH CHO NHÀ PHÁT TRIỂN**

Sử dụng mô-đun này để khiến bot rời khỏi một số cuộc trò chuyện
mà bạn không muốn nó tham gia.

/blacklist_chat [CHAT_ID] - Đưa cuộc trò chuyện vào danh sách cấm.
/whitelist_chat [CHAT_ID] - Cho phép trò chuyện.
/blacklisted - Hiển thị các cuộc trò chuyện bị cấm.
"""


@app.on_message(filters.command("blacklist_chat") & SUDOERS)
@capture_err
async def blacklist_chat_func(_, message: Message):
    if len(message.command) != 2:
        return await message.reply_text(
            "**Cách dùng:**\n/blacklist_chat [CHAT_ID]"
        )
    chat_id = int(message.text.strip().split()[1])
    if chat_id in await blacklisted_chats():
        return await message.reply_text("Trò chuyện đã bị đưa vào danh sách cấm.")
    blacklisted = await blacklist_chat(chat_id)
    if blacklisted:
        return await message.reply_text(
            "Trò chuyện đã được đưa vào danh sách cấm thành công"
        )
    await message.reply_text("Có gì đó không ổn đã xảy ra, hãy kiểm tra nhật ký.")


@app.on_message(filters.command("whitelist_chat") & SUDOERS)
@capture_err
async def whitelist_chat_func(_, message: Message):
    if len(message.command) != 2:
        return await message.reply_text(
            "**Cách dùng:**\n/whitelist_chat [CHAT_ID]"
        )
    chat_id = int(message.text.strip().split()[1])
    if chat_id not in await blacklisted_chats():
        return await message.reply_text("Trò chuyện đã được bỏ cấm.")
    whitelisted = await whitelist_chat(chat_id)
    if whitelisted:
        return await message.reply_text(
            "Trò chuyện đã được bỏ cấm thành công"
        )
    await message.reply_text("Có gì đó không ổn đã xảy ra, hãy kiểm tra nhật ký.")


@app.on_message(filters.command("blacklisted_chats") & SUDOERS)
@capture_err
async def blacklisted_chats_func(_, message: Message):
    text = ""
    for count, chat_id in enumerate(await blacklisted_chats(), 1):
        try:
            title = (await app.get_chat(chat_id)).title
        except Exception:
            title = "Private"
        text += f"**{count}. {title}** [`{chat_id}`]\n"
    if text == "":
        return await message.reply_text("Không tìm thấy cuộc trò chuyện nào bị cấm.")
    await message.reply_text(text)
