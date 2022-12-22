# Setup Mongo DB Atlas Connection
from pymongo import MongoClient
import os
from dotenv import load_dotenv

client = MongoClient(os.getenv('MONGO_DB_KEY'))
db = client.discord_bot
user_collection = db.users
