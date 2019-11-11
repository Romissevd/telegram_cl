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

    def add(self, info):
        self.collection.insert_one(info)

    def __str__(self):
        for val in self.collection.find():
            print(val)
        return str(self.collection.find_one())
