import datetime
import threading
import time

from models import UserModel
from models import MessageModel

from data_structs import create_template
from data_structs import create_view_check
from data_structs import create_quick_reply
from data_structs import create_text_message
from data_structs import create_location_ask
from data_structs import create_type_simulation

from api import call_send_api
from api import call_user_api
from api import call_geosname_api

global_token = None
global_geonames_user = None

MAX_TIME = 60 * 5  # 5 Minutes


def receive_message(event, token, geonames_user):
    sender_id = event['sender']['id']
    message = event['message']

    global global_token, global_geonames_user
    global_token = token
    global_geonames_user = geonames_user

    handle_action(sender_id, message)


def receive_postback(event, token):
    sender_id = event['sender']['id']
    payload = event['postback']['payload']

    global global_token
    global_token = token

    handle_postback(sender_id, payload)


def handle_action(sender_id, message):
    user_data = UserModel.find(user_id=sender_id)

    if user_data is None:
        register_step(sender_id)
    else:
        try_send_message(user_data, message)


def handle_postback(sender_id, payload):
    if payload == 'START_CHAT':
        register_step(sender_id)


def try_send_message(user, message):
    flag = check_last_connection(user)
    is_special_message = validate_quick_reply(user, message)

    if not is_special_message:
        message_content = message.get('text', '')

        if 'HELP' in message_content:
            send_loop_messages(user, 'help', 'help')
        elif 'DEVELOPER' in message_content:
            send_loop_messages(user, 'help', 'developer')
        elif 'FORGET' in message_content:
            UserModel.delete_collection()
            view_check = create_view_check(user)
            call_send_api(view_check, global_token)
        elif not flag:
            send_loop_messages(user, 'not_found', 'not_found')


def check_last_connection(user):
    now = datetime.datetime.now()
    last_message = user.get('last_message', now)

    flag = (now - last_message).seconds >= MAX_TIME
    if flag:
        programming_message(user)
        send_loop_messages(user, 'specific', 'return_user', user)

    user['last_message'] = now
    save_user_async(user)

    return flag


def register_step(sender_id):
    # Get user data
    user_data = call_user_api(sender_id, global_token)
    first_name = user_data['first_name']
    last_name = user_data['last_name']
    gender = user_data['gender']

    # Persist user data
    user = UserModel.new(first_name=first_name,
                         last_name=last_name,
                         gender=gender,
                         user_id=sender_id,
                         created_at=datetime.datetime.now())

    send_loop_messages(user, 'common', 'welcome')


def validate_quick_reply(user, message):
    is_quick_reply = message.get('quick_reply', {})
    has_attachments = message.get('attachments', [])
    if is_quick_reply:
        set_user_reply(user, is_quick_reply)
    elif has_attachments:
        set_user_attachments(user, has_attachments)

    return is_quick_reply or has_attachments


def set_user_reply(user, q_reply):
    if user is not None:
        payload = q_reply['payload']
        preferences = user.get('preferences', [])

        if not preferences or payload not in preferences:
            preferences.append(payload)

        user['preferences'] = payload
        save_user_async(user)
        send_loop_messages(user, 'quick_reply', payload)


def set_user_attachments(user, attachments):
    for attachment in attachments:
        if attachment['type'] == 'location':
            coordinates = attachment['payload']['coordinates']
            lat, lng = coordinates['lat'], coordinates['long']

            set_user_location(user, lat, lng)
            check_actions(user, 'WEATHER')


def set_user_location(user, lat, lng):
    data_model = call_geosname_api(lat, lng, global_geonames_user)

    locations = user.get('locations', [])
    locations.append({
        'lat': lat,
        'lng': lng,
        'city': data_model['city']
    })
    user['locations'] = locations
    save_user_async(user)

    send_loop_messages(user, 'specific', 'WEATHER', data_model)


def check_actions(user, action):
    actions = user.get('actions', [])
    action_done = {action: True}

    if action_done not in actions:
        actions.append(action_done)
        user['actions'] = actions
        save_user_async(user)

        send_loop_messages(user, 'done', action)


def send_loop_messages(user, message_type='', context='', data_model=None):
    messages = MessageModel.find_by_order(type=message_type, context=context)
    for message in messages:
        # Simulate typing
        type_simulation = create_type_simulation(user)
        call_send_api(type_simulation, global_token)
        # Send message
        type_message = get_message_data(user, message, data_model)
        call_send_api(type_message, global_token)


def get_message_data(user, message, data_model):
    type_message = message['type_message']
    if type_message == 'text_message':
        return create_text_message(user, message, data_model)
    elif type_message == 'quick_reply':
        return create_quick_reply(user, message)
    elif type_message == 'quick_reply_location':
        return create_location_ask(user, message)
    elif type_message == 'template':
        return create_template(user, message)


def save_user_async(user):
    def async_method(user_data):
        UserModel.save(user_data)

    async_save = threading.Thread(name='async_method', target=async_method, args=(user, ))
    async_save.start()


def programming_message(user):
    def send_reminder(user_data):
        today = datetime.datetime.today()
        future = datetime.datetime(today.year, today.month, today.day, today.hour, today.minute + 5)
        time.sleep((future - today).seconds)
        send_loop_messages(user_data, 'reminder', 'reminder')

    async_message = threading.Thread(name='send_reminder', target=send_reminder, args=(user, ))
    async_message.start()
