import pymongo
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
        self.collection = self.db[self.collection_name]
        # self.collection.create_index([('userid', pymongo.ASCENDING)], unique=True)

    def find(self, filter={}, projection={}, skip=0, limit=0):
        # return list
        return self.collection.find(filter, projection, skip, limit)

    def find_one(self, option={}, select={}):
        return self.collection.find_one(option, select)

    def find_by_id(self, _id):
        return self.collection.find_one({"_id": ObjectId(_id)})

    def bulk_inserts(self, inserts):
        self.collection.insert_many(inserts)

    def update_one(self, filter, update, upsert=False):
        return self.collection.update_one(filter, {'$set': update}, upsert).matched_count

    def replace_one(self, filter, replace, upsert=False):
        return self.collection.replace_one(filter, replace, upsert).modified_count

    def update_many(self, filter, update, upsert=False):
        return self.collection.update_many(filter, {'$set': update}, upsert).modified_count

    def delete_one(self, filter):
        return self.collection.delete_one(filter).deleted_count

    def delete_many(self, filter):
        return self.collection.delete_many(filter).deleted_count

    def find_one_and_delete(self, filter, projection=None, sort=None):
        # The projection option can be used to limit the fields returned.
        # If multiple documents match filter, a sort can be applied  sort=[('_id', pymongo.DESCENDING)]
        return self.collection.find_one_and_delete(filter, projection, sort)

class BaseModel(Model):
    db = Mongo("mongodb://localhost:27017/")
    print('db: ', db)

class UserModel(BaseModel):
    collection_name = 'anchor'

class Journey(BaseModel):
    collection_name = 'journey'

# info = UserModel().find({'name': '晓东'}, {'name': 1})
# for v in info:
#     print('v: ', v)

# info = UserModel().update_one({'userid': '23429241'}, {'follow': 18})
# print('userInfo: ', info)
