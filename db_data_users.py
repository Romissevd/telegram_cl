__author__ = 'Roman Evdokimov'

import pymongo


class MongoDB():

    db_name = 'results'
    collection_name = 'bets'
    host = 'localhost'
    port = 27017

    def __init__(self, collection=collection_name):
        self.client = pymongo.MongoClient(MongoDB.host, MongoDB.port)
        self.db = self.client[MongoDB.db_name]
        self.collection = self.db[collection]

    def set_user_info(self, id_, user_info):
        self.collection.insert_one({'id_telegram': id_, 'user': user_info})

    def get_user_info(self, id_):
        user = self.collection.find_one({'id_telegram': id_})
        if not user:
            return None
        return user['user']

    def __str__(self):
        for val in self.collection.find():
            print(val)
        print('=='*40)
        return str(self.collection.find_one())


if __name__ == '__main__':
    db = MongoDB()