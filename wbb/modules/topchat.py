from pyrogram import filters
from pymongo import MongoClient
from wbb import app
from config import MONGO_DB_URI
from pyrogram.types import *


mongo_client = MongoClient(MONGO_DB_URI)
db = mongo_client["toptrochuyen"]
collection = db["top"]

user_data = {}

today = {}

pic = "https://telegra.ph/file/6589d5e41ccaf809453b7.jpg"


# ------------------- watcher ----------------------- #

@app.on_message(filters.group & filters.group, group=6)
def today_watcher(_, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if chat_id in today and user_id in today[chat_id]:
        today[chat_id][user_id]["total_messages"] += 1
    else:
        if chat_id not in today:
            today[chat_id] = {}
        if user_id not in today[chat_id]:
            today[chat_id][user_id] = {"total_messages": 1}
        else:
            today[chat_id][user_id]["total_messages"] = 1


@app.on_message(filters.group & filters.group, group=11)
def _watcher(_, message):
    user_id = message.from_user.id    
    user_data.setdefault(user_id, {}).setdefault("total_messages", 0)
    user_data[user_id]["total_messages"] += 1    
    collection.update_one({"_id": user_id}, {"$inc": {"total_messages": 1}}, upsert=True)


# ------------------- ranks ------------------ #

@app.on_message(filters.command("topmom"))
async def today_(_, message):
    chat_id = message.chat.id
    if chat_id in today:
        users_data = [(user_id, user_data["total_messages"]) for user_id, user_data in today[chat_id].items()]
        sorted_users_data = sorted(users_data, key=lambda x: x[1], reverse=True)[:10]
        
        if sorted_users_data:
            response = "**📈 TOP MÕM**\n"
            for idx, (user_id, total_messages) in enumerate(sorted_users_data, start=1):
                try:
                    user_name = (await app.get_users(user_id)).first_name
                except:
                    user_name = "Unknown"
                user_info = f"**{idx}**. {user_name} • {total_messages}\n"
                response += user_info
            button = InlineKeyboardMarkup(
                [[    
                   InlineKeyboardButton("TOP MÕM TOÀN SERVER", callback_data="overall"),
                ]])
            await message.reply_photo(photo=pic, caption=response, reply_markup=button)
        else:
            await message.reply_text("Không có dữ liệu hôm nay.")
    else:
        await message.reply_text("Không có dữ liệu hôm nay.")



@app.on_message(filters.command("topsv"))
async def ranking(_, message):
    top_members = collection.find().sort("total_messages", -1).limit(10)
    
    response = "**📈 TOP MÕM TOÀN SERVER**\n"
    for idx, member in enumerate(top_members, start=1):
        user_id = member["_id"]
        total_messages = member["total_messages"]
        try:
            user_name = (await app.get_users(user_id)).first_name
        except:
            user_name = "Unknown"
        
        user_info = f"**{idx}**. {user_name} • {total_messages}\n"
        response += user_info 
    button = InlineKeyboardMarkup(
            [[    
               InlineKeyboardButton("TOP MÕM", callback_data="today"),
            ]])
    await message.reply_photo(photo=pic, caption=response, reply_markup=button)



# -------------------- regex -------------------- # 

@app.on_callback_query(filters.regex("today"))
async def today_rank(_, query):
    chat_id = query.message.chat.id
    if chat_id in today:
        users_data = [(user_id, user_data["total_messages"]) for user_id, user_data in today[chat_id].items()]
        sorted_users_data = sorted(users_data, key=lambda x: x[1], reverse=True)[:10]
        
        if sorted_users_data:
            response = "**📈 TOP MÕM**\n"
            for idx, (user_id, total_messages) in enumerate(sorted_users_data, start=1):
                try:
                    user_name = (await app.get_users(user_id)).first_name
                except:
                    user_name = "Unknown"
                user_info = f"**{idx}**. {user_name} • {total_messages}\n"
                response += user_info
            button = InlineKeyboardMarkup(
                [[    
                   InlineKeyboardButton("TOP MÕM TOÀN SERVER", callback_data="overall"),
                ]])
            await query.message.edit_text(response, reply_markup=button)
        else:
            await query.answer("Không có dữ liệu hôm nay.")
    else:
        await query.answer("Không có dữ liệu hôm nay.")



@app.on_callback_query(filters.regex("overall"))
async def overall_rank(_, query):
    top_members = collection.find().sort("total_messages", -1).limit(10)
    
    response = "**📈 TOP MÕM TOÀN SERVER**\n"
    for idx, member in enumerate(top_members, start=1):
        user_id = member["_id"]
        total_messages = member["total_messages"]
        try:
            user_name = (await app.get_users(user_id)).first_name
        except:
            user_name = "Unknown"
        
        user_info = f"**{idx}**. {user_name} • {total_messages}\n"
        response += user_info 
    button = InlineKeyboardMarkup(
            [[    
               InlineKeyboardButton("TOP MÕM", callback_data="today"),
            ]])
    await query.message.edit_text(response, reply_markup=button)




    

    
