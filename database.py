from pymongo import AsyncMongoClient
import os

MONGO_URL = os.getenv("MONGO_DB_URL")

client = AsyncMongoClient(MONGO_URL)

db = client["auth_db"]
db2 = client["chat_db"]

users_collection = db["users"]

messages_collection = db2["messages"]

session_collection = db2["chat_sessions"]
