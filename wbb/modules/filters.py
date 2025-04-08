"""
MIT License

Copyright (c) 2024 TheHamkerCat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import re

from pyrogram import filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from wbb import app
from wbb.core.decorators.errors import capture_err
from wbb.core.decorators.permissions import adminsOnly
from wbb.core.keyboard import ikb
from wbb.modules.admin import member_permissions
from wbb.modules.notes import extract_urls
from wbb.utils.dbfunctions import (
    delete_filter,
    deleteall_filters,
    get_filter,
    get_filters_names,
    save_filter,
)
from wbb.utils.filter_groups import chat_filters_group
from wbb.utils.functions import (
    check_format,
    extract_text_and_keyb,
    get_data_and_name,
)

__MODULE__ = "Filters"
__HELP__ = """/filters Để có được tất cả các bộ lọc trong cuộc trò chuyện.
/filter [FILTER_NAME] Để Lưu Bộ Lọc (trả lời tin nhắn).

Các loại bộ lọc được hỗ trợ là Văn bản, Hoạt hình, Ảnh, Tài liệu, Video, ghi chú video, Âm thanh, Giọng nói.

Để sử dụng nhiều từ hơn trong bộ lọc, hãy sử dụng.
`/filter Hey_there` Để lọc "Hey there".

/stop [FILTER_NAME] Để dừng một bộ lọc.
/stopall Để xóa tất cả các bộ lọc trong một cuộc trò chuyện (vĩnh viễn).

Bạn cũng có thể sử dụng markdown hoặc html để lưu văn bản.

Kiểm tra /markdownhelp để biết thêm về định dạng và cú pháp khác.
"""


@app.on_message(filters.command("filter") & ~filters.private)
@adminsOnly("can_change_info")
async def save_filters(_, message):
    try:
        if len(message.command) < 2:
            return await message.reply_text(
                "**Cách dùng:**\nTrả lời tin nhắn với /filter [FILTER_NAME] [NỘI DUNG] Để thiết lập bộ lọc mới."
            )
        replied_message = message.reply_to_message
        if not replied_message:
            replied_message = message
        data, name = await get_data_and_name(replied_message, message)
        if data == "error":
            return await message.reply_text(
                "**Cách dùng:**\n__/filter [FILTER_NAME] [NỘI DUNG]__\n`-----------Hoặc-----------`\nTrả lời tin nhắn với.\n/filter [FILTER_NAME]."
            )
        if replied_message.text:
            _type = "text"
            file_id = None
        if replied_message.sticker:
            _type = "sticker"
            file_id = replied_message.sticker.file_id
        if replied_message.animation:
            _type = "animation"
            file_id = replied_message.animation.file_id
        if replied_message.photo:
            _type = "photo"
            file_id = replied_message.photo.file_id
        if replied_message.document:
            _type = "document"
            file_id = replied_message.document.file_id
        if replied_message.video:
            _type = "video"
            file_id = replied_message.video.file_id
        if replied_message.video_note:
            _type = "video_note"
            file_id = replied_message.video_note.file_id
        if replied_message.audio:
            _type = "audio"
            file_id = replied_message.audio.file_id
        if replied_message.voice:
            _type = "voice"
            file_id = replied_message.voice.file_id
        if replied_message.reply_markup and not re.findall(r"\[.+\,.+\]", data):
            urls = extract_urls(replied_message.reply_markup)
            if urls:
                response = "\n".join(
                    [f"{name}=[{text}, {url}]" for name, text, url in urls]
                )
                data = data + response
        if data:
            data = await check_format(ikb, data)
            if not data:
                return await message.reply_text(
                    "**Định dạng không đúng, hãy kiểm tra phần trợ giúp.**"
                )
        name = name.replace("_", " ")
        _filter = {
            "type": _type,
            "data": data,
            "file_id": file_id,
        }
        chat_id = message.chat.id
        await save_filter(chat_id, name, _filter)
        return await message.reply_text(f"__**Bộ lọc đã lưu {name}.**__")
    except UnboundLocalError:
        return await message.reply_text(
            "**Tin nhắn đã trả lời không thể truy cập được.\n`Chuyển tiếp tin nhắn và thử lại`**"
        )


@app.on_message(filters.command("filters") & ~filters.private)
@capture_err
async def get_filterss(_, message):
    _filters = await get_filters_names(message.chat.id)
    if not _filters:
        return await message.reply_text("**Không có bộ lọc trong cuộc trò chuyện này.**")
    _filters.sort()
    msg = f"Danh sách các bộ lọc trong {message.chat.title} :\n"
    for _filter in _filters:
        msg += f"**-** `{_filter}`\n"
    await message.reply_text(msg)


@app.on_message(filters.command("stop") & ~filters.private)
@adminsOnly("can_change_info")
async def del_filter(_, message):
    if len(message.command) < 2:
        return await message.reply_text("**Cách dùng:**\n__/stop [FILTER_NAME]__")
    name = message.text.split(None, 1)[1].strip()
    if not name:
        return await message.reply_text("**Cách dùng:**\n__/stop [FILTER_NAME]__")
    chat_id = message.chat.id
    deleted = await delete_filter(chat_id, name)
    if deleted:
        await message.reply_text(f"**Bộ lọc đã xóa {name}.**")
    else:
        await message.reply_text("**Không có bộ lọc nào như vậy.**")


@app.on_message(
    filters.text & ~filters.private & ~filters.channel & ~filters.via_bot & ~filters.forwarded,
    group=chat_filters_group,
)
@capture_err
async def filters_re(_, message):
    from_user = message.from_user if message.from_user else message.sender_chat
    user_id = from_user.id
    chat_id = message.chat.id
    text = message.text.lower().strip()
    if not text:
        return
    chat_id = message.chat.id
    list_of_filters = await get_filters_names(chat_id)
    for word in list_of_filters:
        pattern = r"( |^|[^\w])" + re.escape(word) + r"( |$|[^\w])"
        if re.search(pattern, text, flags=re.IGNORECASE):
            _filter = await get_filter(chat_id, word)
            data_type = _filter["type"]
            data = _filter["data"]
            file_id = _filter.get("file_id")
            keyb = None
            if data:
                if "{chat}" in data:
                    data = data.replace(
                        "{chat}", message.chat.title
                    )
                if "{name}" in data:
                    data = data.replace(
                        "{name}", (from_user.mention if message.from_user else from_user.title)
                    )
                if re.findall(r"\[.+\,.+\]", data):
                    keyboard = extract_text_and_keyb(ikb, data)
                    if keyboard:
                        data, keyb = keyboard
            replied_message = message.reply_to_message
            if replied_message:
                replied_user = replied_message.from_user if replied_message.from_user else replied_message.sender_chat
                if text.startswith("~"):
                    await message.delete()
                if replied_user.id != from_user.id:
                    message = replied_message

            if data_type == "text":
                await message.reply_text(
                    text=data,
                    reply_markup=keyb,
                    disable_web_page_preview=True,
                )
            else:
                if not file_id:
                    continue
            if data_type == "sticker":
                await message.reply_sticker(
                    sticker=file_id,
                )
            if data_type == "animation":
                await message.reply_animation(
                    animation=file_id,
                    caption=data,
                    reply_markup=keyb,
                )
            if data_type == "photo":
                await message.reply_photo(
                    photo=file_id,
                    caption=data,
                    reply_markup=keyb,
                )
            if data_type == "document":
                await message.reply_document(
                    document=file_id,
                    caption=data,
                    reply_markup=keyb,
                )
            if data_type == "video":
                await message.reply_video(
                    video=file_id,
                    caption=data,
                    reply_markup=keyb,
                )
            if data_type == "video_note":
                await message.reply_video_note(
                    video_note=file_id,
                )
            if data_type == "audio":
                await message.reply_audio(
                    audio=file_id,
                    caption=data,
                    reply_markup=keyb,
                )
            if data_type == "voice":
                await message.reply_voice(
                    voice=file_id,
                    caption=data,
                    reply_markup=keyb,
                )
            return  # NOTE: Avoid filter spam


@app.on_message(filters.command("stopall") & ~filters.private)
@adminsOnly("can_change_info")
async def stop_all(_, message):
    _filters = await get_filters_names(message.chat.id)
    if not _filters:
        await message.reply_text("**Không có bộ lọc trong cuộc trò chuyện này.**")
    else:
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Đúng, hãy làm đi", callback_data="stop_yes"
                    ),
                    InlineKeyboardButton("Hủy", callback_data="stop_no"),
                ]
            ]
        )
        await message.reply_text(
            "**Bạn có chắc chắn muốn xóa tất cả các bộ lọc trong cuộc trò chuyện này mãi mãi không?.**",
            reply_markup=keyboard,
        )


@app.on_callback_query(filters.regex("stop_(.*)"))
async def stop_all_cb(_, cb):
    chat_id = cb.message.chat.id
    from_user = cb.from_user
    permissions = await member_permissions(chat_id, from_user.id)
    permission = "can_change_info"
    if permission not in permissions:
        return await cb.answer(
            f"Bạn không có quyền cần thiết.\n Quyền: {permission}",
            show_alert=True,
        )
    input = cb.data.split("_", 1)[1]
    if input == "yes":
        stoped_all = await deleteall_filters(chat_id)
        if stoped_all:
            return await cb.message.edit(
                "**Đã xóa thành công tất cả các bộ lọc trên cuộc trò chuyện này.**"
            )
    if input == "no":
        await cb.message.reply_to_message.delete()
        await cb.message.delete()
