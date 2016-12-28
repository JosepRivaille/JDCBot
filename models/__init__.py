import json
import os

from pymongo import MongoClient

from user import User
from message import Message


def get_path():
    return os.path.dirname(os.path.realpath(__file__))


def pluralize_class(instance):
    return ("{class_name}s".format(class_name=instance.__class__.__name__)).lower()


def load_data(model, folder='data'):
    path = "{path}/{folder}/{jsonfile}.json".format(path=get_path(),
                                                    folder=folder,
                                                    jsonfile=pluralize_class(model))

    with open(path) as f:
        data = json.load(f)
        for json_data in data:
            model.save(json_data)

URL = 'localhost'
PORT = 27017
USERS_COLLECTION = 'users'
MESSAGES_COLLECTION = 'messages'

client = MongoClient(URL, PORT)
database = client.jdcbot

UserModel = User(database, USERS_COLLECTION)
UserModel.delete_collection()

MessageModel = Message(database, MESSAGES_COLLECTION)
MessageModel.delete_collection()
load_data(MessageModel)
