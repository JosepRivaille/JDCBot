from structs import simulate_message_typing
from structs import check_message_viewed
from structs import text_message
from structs import item_quick_reply
from structs import quick_reply
from structs import quick_reply_location
from structs import template_message_generic


def create_type_simulation(user):
    return simulate_message_typing(user['user_id'])


def create_view_check(user):
    return check_message_viewed(user['user_id'])


def create_text_message(user, data, data_model):
    message = data['content']
    if 'format' in data:
        message = message.format(**data_model) if 'data_model' in data else message.format(**user)
    return text_message(user['user_id'], message)


def create_quick_reply(user, data):
    replies = []
    for reply in data['replies']:
        item = item_quick_reply(reply['title'], reply['payload'])
        replies.append(item)
    return quick_reply(user['user_id'], data['content'], replies)


def create_location_ask(user, data):
    return quick_reply_location(user['user_id'], data['content'])


def create_template(user, data):
    return template_message_generic(user['user_id'], data['elements'])
