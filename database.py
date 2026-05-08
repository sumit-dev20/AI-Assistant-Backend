from pymongo import AsyncMongoClient
import os

MONGO_URL = os.getenv("MONGO_DB_URL")

client = AsyncMongoClient(MONGO_URL)

db = client["auth_db"]

users_collection = db["users"]
