import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId

class Mongo():
    def __new__(cls, *args, **kwargs):
        client = MongoClient(str(*args))
        db = client['huajiao']
        return db
    def __del__(self):
        self.client.close()

class Model():
    def __init__(self):
        print('collection_name: ', self.collection_name)
        self.collection = self.db[self.collection_name]

    def find(self, option={}, select={}):
        # return list
        return self.collection.find(option, select)

    def find_one(self, option={}, select={}):
        return self.collection.find_one(option, select)

    def find_by_id(self, _id):
        return self.collection.find_one({"_id": ObjectId(_id)})

    def bulk_insterts(self, inserts):
        self.collection.insert_many(inserts)


class BaseModel(Model):
    db = Mongo("mongodb://localhost:27017/")
    print('db: ', db)

class UserModel(BaseModel):
    collection_name = 'anchor'


# info = UserModel().find({'name': '晓东'}, {'name': 1})
# for v in info:
#     print('v: ', v)

# info = UserModel().find_one({'name': '晓东'}, {'name': 1})
# print('userInfo: ', info)
