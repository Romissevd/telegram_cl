__author__ = 'Roman Evdokimov'

import datetime

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
        self.collection.insert_one({
            'id_telegram': id_,
            'user': user_info,
            'date_registration': datetime.datetime.now(),
        })

    def get_user_info(self, id_):
        user = self.collection.find_one({'id_telegram': id_})
        if not user:
            return None
        return user['user']

    def update_user_info(self, id_, user_info):
        self.collection.update_one({'id_telegram': id_}, {'$set': {'user': user_info}})

    def set_matches(self):
        pass

    def get_matches(self):
        pass

    def change_result_matches(self):
        pass

    def __str__(self):
        for val in self.collection.find():
            print(val)
        print('=='*40)
        return str(self.collection.find_one())


if __name__ == '__main__':
    db = MongoDB()