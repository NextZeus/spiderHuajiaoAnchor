import datetime
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")

db = client['huajiao']

collection = db['anchor']

info = {
    "username": "Mike",
    "text": "My First Blog",
    "tags": ["mongodb", "python", "pymongo"],
    "date": datetime.datetime.utcnow()
}


info_id = collection.insert_one(info).inserted_id

print('info_id: ', info_id)
