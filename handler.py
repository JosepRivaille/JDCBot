import requests
import json

from models import UserModel
from models import MessageModel

from data_structs import *

global_token = None


def receive_message(event, token):
    sender_id = event['sender']['id']
    message = event['message']

    global global_token
    global_token = token

    handle_action(sender_id, message)


def handle_action(sender_id, message):
    user_data = UserModel.find(user_id=sender_id)
    validate_quick_reply(user_data, message)

    if user_data is None:
        user = register_step(sender_id)
        send_loop_messages(user, 'common', 'welcome')
    elif message.get('text', '') == 'FORGET':
        UserModel.delete_collection()
    else:
        message = 'Sorry {}, this is all at the moment :('.format(user_data['first_name'])
        message = text_message(sender_id, message)
        call_send_api(message)


def register_step(sender_id):
    # Get user data
    user_data = call_user_api(sender_id)
    first_name = user_data['first_name']
    last_name = user_data['last_name']
    gender = user_data['gender']

    # Persist user data
    return UserModel.new(first_name=first_name,
                         last_name=last_name,
                         gender=gender,
                         user_id=sender_id)


def validate_quick_reply(user, message):
    is_quick_reply = message.get('quick_reply', {})
    has_attachments = message.get('attachments', [])
    if is_quick_reply:
        set_user_reply(user, is_quick_reply)
    elif has_attachments:
        set_user_attachments(user, has_attachments)


def set_user_reply(user, q_reply):
    if user is not None:
        payload = q_reply['payload']
        preferences = user.get('preferences', [])

        if not preferences or payload not in preferences:
            preferences.append(payload)

        user['preferences'] = payload
        UserModel.save(user)
        send_loop_messages(user, 'quick_reply', payload)


def set_user_attachments(user, attachments):
    for attachment in attachments:
        if attachment['type'] == 'location':
            coordinates = attachment['payload']['coordinates']
            lat, long = coordinates['lat'], coordinates['long']
            print(lat, long)


def send_loop_messages(user, message_type='', context=''):
    messages = MessageModel.find_by_order(type=message_type, context=context)
    for message in messages:
        # Simulate typing
        type_simulation = create_type_simulation(user)
        call_send_api(type_simulation)
        # Send message
        type_message = get_message_data(user, message)
        call_send_api(type_message)


def get_message_data(user, message):
    type_message = message['type_message']
    if type_message == 'text_message':
        return create_text_message(user, message)
    elif type_message == 'quick_reply':
        return create_quick_reply(user, message)


def call_send_api(data):
    response = requests.post('https://graph.facebook.com/v2.6/me/messages',
                             params={'access_token': global_token},
                             data=json.dumps(data),
                             headers={'Content-type': 'application/json'})
    if response.status_code == 200:
        print('Message sent successfully')
    else:
        print('Error: ' + str(response.status_code))


def call_user_api(user_id):
    response = requests.get('https://graph.facebook.com/v2.6/' + user_id,
                            params={'access_token': global_token})

    if response.status_code == 200:
        return json.loads(response.text)
    else:
        print('Error: ' + str(response.status_code))
        return None
