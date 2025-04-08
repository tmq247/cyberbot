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
import os

from pyrogram import filters

from wbb import app
from wbb.core.decorators.permissions import adminsOnly

__MODULE__ = "Admin Miscs"
__HELP__ = """
/doitennhom - Thay đổi tên của một nhóm/kênh.
/doianhnhom - Thay đổi ảnh đại diện của một nhóm/kênh.
/tenqtv - Thay đổi chức danh quản trị viên của một quản trị viên.
"""


@app.on_message(filters.command("doitennhom") & ~filters.private)
@adminsOnly("can_change_info")
async def set_chat_title(_, message):
    if len(message.command) < 2:
        return await message.reply_text("**Cách sử dụng:**\n/doitennhom TÊN MỚI")
    old_title = message.chat.title
    new_title = message.text.split(None, 1)[1]
    await message.chat.set_title(new_title)
    await message.reply_text(
        f"Đã thay đổi thành công tiêu đề nhóm từ {old_title} Thành {new_title}"
    )


@app.on_message(filters.command("tenqtv") & ~filters.private)
@adminsOnly("can_change_info")
async def set_user_title(_, message):
    if not message.reply_to_message:
        return await message.reply_text(
            "Trả lời tin nhắn của người dùng để đặt chức danh quản trị viên của anh ta"
        )
    if not message.reply_to_message.from_user:
        return await message.reply_text(
            "Tôi không thể thay đổi tiêu đề quản trị viên của một thực thể không xác định"
        )
    chat_id = message.chat.id
    from_user = message.reply_to_message.from_user
    if len(message.command) < 2:
        return await message.reply_text(
            "**Cách sử dụng:**\n/set_user_title CHỨC DANH QUẢN TRỊ VIÊN MỚI"
        )
    title = message.text.split(None, 1)[1]
    await app.set_administrator_title(chat_id, from_user.id, title)
    await message.reply_text(
        f"Successfully Changed {from_user.mention}'s Admin Title To {title}"
    )


@app.on_message(filters.command("doianhnhom") & ~filters.private)
@adminsOnly("can_change_info")
async def set_chat_photo(_, message):
    reply = message.reply_to_message

    if not reply:
        return await message.reply_text(
            "Trả lời một bức ảnh để đặt nó thành ảnh đại diện nhóm"
        )

    file = reply.document or reply.photo
    if not file:
        return await message.reply_text(
            "Trả lời ảnh hoặc tài liệu để đặt nó thành ảnh đại diện nhóm"
        )

    if file.file_size > 5000000:
        return await message.reply("Kích thước tập tin quá lớn.")

    photo = await reply.download()
    await message.chat.set_photo(photo)
    await message.reply_text("Đã thay đổi ảnh nhóm thành công")
    os.remove(photo)
