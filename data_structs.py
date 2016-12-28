from structs import *


def create_type_simulation(user):
    return simulate_message_typing(user['user_id'])


def create_text_message(user, data):
    return text_message(user['user_id'], data['content'])


def create_quick_reply(user, data):
    replies = []
    for reply in data['replies']:
        item = item_quick_reply(reply['title'], reply['payload'])
        replies.append(item)
    return quick_reply(user['user_id'], data['content'], replies)
