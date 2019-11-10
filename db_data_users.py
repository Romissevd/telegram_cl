__author__ = 'Roman Evdokimov'

import pymongo

conn = pymongo.MongoClient('localhost', 27017)
db = conn.test_database
