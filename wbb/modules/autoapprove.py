"""
MIT License

Copyright (c) 2024 SI_NN_ER_LS 

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

from pyrogram import filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.types import (
    CallbackQuery,
    Chat,
    ChatJoinRequest,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from wbb import SUDOERS, app, db
from wbb.core.decorators.permissions import adminsOnly
from wbb.core.keyboard import ikb
from wbb.modules.admin import member_permissions
from wbb.modules.greetings import handle_new_member, send_welcome_message

approvaldb = db.autoapprove

__MODULE__ = "Autoapprove"
__HELP__ = """
command: /autoapprove

Mô-đun này giúp tự động chấp nhận yêu cầu tham gia trò chuyện được gửi bởi người dùng thông qua liên kết lời mời của nhóm bạn

**Chế độ:**
¤ Tự động - Tự động chấp nhận yêu cầu tham gia trò chuyện.

¤ Hướng dẫn - Một tin nhắn sẽ được gửi đến cuộc trò chuyện bằng cách gắn thẻ người quản trị. Người quản trị có thể chấp nhận hoặc từ chối yêu cầu.

Dùng: /clear_pending Lệnh xóa tất cả ID người dùng đang chờ xử lý khỏi DB. Điều này sẽ cho phép người dùng gửi lại yêu cầu.
"""


@app.on_message(filters.command("autoapprove") & filters.group)
@adminsOnly("can_change_info")
async def approval_command(client, message):
    chat_id = message.chat.id
    chat = await approvaldb.find_one({"chat_id": chat_id})
    if chat:
        mode = chat.get("mode", "")
        if not mode:
            mode = "automatic"
            await approvaldb.update_one(
                {"chat_id": chat_id},
                {"$set": {"mode": mode}},
                upsert=True,
            )
        if mode == "automatic":
            switch = "manual"
        else:
            switch = "automatic"
        buttons = {
            "Turn OFF": "approval_off",
            f"{(mode.upper())}": f"approval_{switch}",
        }
        keyboard = ikb(buttons, 1)
        await message.reply(
            "**Tự động phê duyệt cho cuộc trò chuyện này: Đã bật.**", reply_markup=keyboard
        )
    else:
        buttons = {"Bật": "approval_on"}
        keyboard = ikb(buttons, 1)
        await message.reply(
            "**Tự động phê duyệt cho cuộc trò chuyện này: Đã tắt.**", reply_markup=keyboard
        )


@app.on_callback_query(filters.regex("approval(.*)"))
async def approval_cb(client, cb):
    chat_id = cb.message.chat.id
    from_user = cb.from_user
    permissions = await member_permissions(chat_id, from_user.id)
    permission = "can_restrict_members"
    if permission not in permissions:
        if from_user.id not in SUDOERS:
            return await cb.answer(
                f"Bạn không có quyền cần thiết.\n Quyền hạn: {permission}",
                show_alert=True,
            )
    command_parts = cb.data.split("_", 1)
    option = command_parts[1]
    if option == "off":
        if await approvaldb.count_documents({"chat_id": chat_id}) > 0:
            approvaldb.delete_one({"chat_id": chat_id})
            buttons = {"Bật": "approval_on"}
            keyboard = ikb(buttons, 1)
            return await cb.edit_message_text(
                "**Tự động phê duyệt cho cuộc trò chuyện này: Đã tắt.**",
                reply_markup=keyboard,
            )
    if option == "on":
        switch = "manual"
        mode = "automatic"
    if option == "automatic":
        switch = "manual"
        mode = option
    if option == "manual":
        switch = "automatic"
        mode = option
    await approvaldb.update_one(
        {"chat_id": chat_id},
        {"$set": {"mode": mode}},
        upsert=True,
    )
    chat = await approvaldb.find_one({"chat_id": chat_id})
    mode = chat["mode"].upper()
    buttons = {"Tắt": "approval_off", f"{mode}": f"approval_{switch}"}
    keyboard = ikb(buttons, 1)
    await cb.edit_message_text(
        "**Tự động phê duyệt cho cuộc trò chuyện này: Đã bật.**", reply_markup=keyboard
    )


@app.on_message(filters.command("clear_pending") & filters.group)
@adminsOnly("can_restrict_members")
async def clear_pending_command(client, message):
    chat_id = message.chat.id
    result = await approvaldb.update_one(
        {"chat_id": chat_id},
        {"$set": {"pending_users": []}},
    )
    if result.modified_count > 0:
        await message.reply_text("Đã xóa người dùng đang chờ xử lý.")
    else:
        await message.reply_text("Không có người dùng đang chờ xóa.")


@app.on_chat_join_request(filters.group)
async def accept(client, message: ChatJoinRequest):
    chat = message.chat
    user = message.from_user
    chat_id = await approvaldb.find_one({"chat_id": chat.id})
    if chat_id:
        mode = chat_id["mode"]
        if mode == "automatic":
            await app.approve_chat_join_request(
                chat_id=chat.id, user_id=user.id
            )
            return await handle_new_member(user, chat)
        if mode == "manual":
            is_user_in_pending = await approvaldb.count_documents(
                {"chat_id": chat.id, "pending_users": int(user.id)}
            )
            if is_user_in_pending == 0:
                await approvaldb.update_one(
                    {"chat_id": chat.id},
                    {"$addToSet": {"pending_users": int(user.id)}},
                    upsert=True,
                )
                buttons = {
                    "accept": f"manual_approve_{user.id}",
                    "Decline": f"manual_decline_{user.id}",
                }
                keyboard = ikb(buttons, int(2))
                text = f"**Người dùng: {user.mention} đã gửi yêu cầu tham gia nhóm của chúng tôi. Bất kỳ quản trị viên nào cũng có thể chấp nhận hoặc từ chối.**"
                admin_data = [
                    i
                    async for i in app.get_chat_members(
                        chat_id=message.chat.id,
                        filter=ChatMembersFilter.ADMINISTRATORS,
                    )
                ]
                for admin in admin_data:
                    if admin.user.is_bot or admin.user.is_deleted:
                        continue
                    text += f"[\u2063](tg://user?id={admin.user.id})"
                return await app.send_message(
                    chat.id, text, reply_markup=keyboard
                )


@app.on_callback_query(filters.regex("manual_(.*)"))
async def manual(app, cb):
    chat = cb.message.chat
    from_user = cb.from_user
    permissions = await member_permissions(chat.id, from_user.id)
    permission = "can_restrict_members"
    if permission not in permissions:
        if from_user.id not in SUDOERS:
            return await cb.answer(
                f"Bạn không có quyền cần thiết.\n Quyền hạn: {permission}",
                show_alert=True,
            )
    datas = cb.data.split("_", 2)
    dis = datas[1]
    id = datas[2]
    if dis == "approve":
        await app.approve_chat_join_request(chat_id=chat.id, user_id=id)
        # No need to verify user as admin is the one who accept the request
    if dis == "decline":
        await app.decline_chat_join_request(chat_id=chat.id, user_id=id)
    await approvaldb.update_one(
        {"chat_id": chat.id},
        {"$pull": {"pending_users": int(id)}},
    )
    return await cb.message.delete()
