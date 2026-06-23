from pymongo import MongoClient

MONGO_URI = "mongodb+srv://aradhanakumari2602:ara_dhana_201@student-progress.jtaeu1a.mongodb.net/?appName=student-progress"

client = MongoClient(MONGO_URI)

db = client["nids_db"]

print("Connected Successfully!")