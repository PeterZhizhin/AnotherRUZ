# -*- coding: utf-8 -*-
import pymongo
from . import mongo_config


class UsersDatabases:
    def __init__(self, users_collection):
        self.users_collection = users_collection
        self.users_collection.create_index([('id', pymongo.ASCENDING)])

    def get_user(self, user_id):
        return self.users_collection.find_one({'id': user_id})

    def add_user(self, user_id):
        self.users_collection.insert({'id': user_id})

    def set_email(self, user_id, email):
        self.users_collection.update_one({'id': user_id},
                                         {'$set': {'email': email}})

    def set_main_menu_message(self, user_id, message_id):
        self.users_collection.update_one({'id': user_id},
                                         {'$set': {'main_menu_message': message_id}})


class Databases:
    def __init__(self):
        self.db = pymongo.MongoClient(host=mongo_config.mongo_host,
                                      port=mongo_config.mongo_port)[mongo_config.database_name]

        self.users_db = UsersDatabases(self.db[mongo_config.users_collection])

    def get_users_db(self):
        return self.users_db
