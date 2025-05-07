from contextlib import suppress
from time import time
from pyrogram import Client, filters
from pymongo import MongoClient
from wbb import app, app2, db
from config import MONGO_URL
from datetime import datetime, timedelta
#import traceback
from pyrogram.types import *


#mongo_client = MongoClient(MONGO_URL)
mongo_client = MongoClient(MONGO_URL)
db = mongo_client["telegram_stats"]
print(db) 
collection = db["message_counts"]


def update_message_count(user_id, chat_id):
    """ Cập nhật số lượng tin nhắn theo tuần/tháng trong MongoDB cho từng nhóm """
    now = datetime.now()
    
    user_data = collection.find_one({"user_id": user_id, "chat_id": chat_id})

    if user_data:
        collection.update_one(
            {"user_id": user_id, "chat_id": chat_id},
            {"$inc": {"weekly_count": 1, "monthly_count": 1}, "$set": {"last_updated": now}}
        )
    else:
        collection.insert_one(
            {"user_id": user_id, "chat_id": chat_id, "weekly_count": 1, "monthly_count": 1, "last_updated": now}
        )

@app.on_message(filters.group & ~filters.bot)
def track_messages(client, message):
    """ Theo dõi tin nhắn mới trong bất kỳ nhóm nào và cập nhật thống kê vào MongoDB """
    update_message_count(message.from_user.id, message.chat.id)

@app.on_message(filters.command("top", prefixes=["/", "!"]) & filters.group)
async def send_top10(client, message):
    
    """ Gửi danh sách top 10 người nhắn nhiều nhất khi có lệnh /top10 trong nhóm hiện tại """
    chat_id = message.chat.id
    now = datetime.now()

    top_weekly = collection.find({"chat_id": chat_id}).sort("weekly_count", -1).limit(10)
    top_monthly = collection.find({"chat_id": chat_id}).sort("monthly_count", -1).limit(10)
    if not top_weekly or not top_monthly:
        await message.reply("Không có dữ liệu tin nhắn trong tuần hoặc tháng này.")
        return

    message_text = "🏆 **Top 10 người nhắn nhiều nhất:**\n\n"
    message_text += "**📅 Trong tuần:**\n" + "\n".join([f"- [{user['user_id']}](tg://user?id={user['user_id']}): {user['weekly_count']} tin nhắn" for user in top_weekly])
    message_text += "\n\n**🗓 Trong tháng:**\n" + "\n".join([f"- [{user['user_id']}](tg://user?id={user['user_id']}): {user['monthly_count']} tin nhắn" for user in top_monthly])
    #await app.send_message(message.chat.id, message_text, disable_web_page_preview=True)
    try:
        print(app)
        await app.send_message(message.chat.id, message_text, disable_web_page_preview=True)
    except Exception as e:
        print("Lỗi:", e)
        traceback.print_exc()
