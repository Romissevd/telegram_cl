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

    def set_matches(self, id_, list_matches):
        for match in list_matches:
            self.collection.update_one({'id_telegram': id_}, {'$push': {'matches': {'date': match['date'],
                                                                                    'match': match['match'],
                                                                                    'result': ''}}})

    def get_matches(self, id_):
        user = self.collection.find_one({'id_telegram': id_})
        list_matches = []
        matches = user.get('matches', None)
        if matches:
            for match in matches:
                if match['date'] > datetime.datetime.now():
                    list_matches.append(match)
            return list_matches
        else:
            return None

    def get_result_match(self, id_, match):
        try:
            find_match = self.collection.find_one({'id_telegram': id_, 'matches.match': match}, {'matches.$.result': 1})
            result_match = find_match['matches'][0]['result']
        except:
            result_match = None
        return result_match

    def get_results_matches(self, id_):
        list_results_matches = []
        for match in self.collection.find_one({'id_telegram': id_})['matches']:
            if match['result']:
                list_results_matches.append(match)
        return list_results_matches

    def change_result_matches(self, id_, match, result):
        self.collection.update_one({'id_telegram': id_, 'matches.match': match}, {'$set': {'matches.$.result': result}})

    def get_text_list_matches(self, id_):
        text = ''
        for match in self.get_matches(id_):
            text += match['match'] + '\n'
        return text

    def __str__(self):
        for val in self.collection.find():
            print(val)
        print('=='*40)
        return str(self.collection.find_one())


if __name__ == '__main__':
    db = MongoDB()