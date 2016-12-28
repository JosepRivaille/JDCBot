import requests
import json

from models import UserModel
from models import MessageModel

from data_structs import *

global_token = None
global_geonames_user = None


def receive_message(event, token, geonames_user):
    sender_id = event['sender']['id']
    message = event['message']

    global global_token, global_geonames_user
    global_token = token
    global_geonames_user = geonames_user

    handle_action(sender_id, message)


def handle_action(sender_id, message):
    user_data = UserModel.find(user_id=sender_id)

    if user_data is None:
        user = register_step(sender_id)
        send_loop_messages(user, 'common', 'welcome')
    elif message.get('text', '') == 'FORGET':
        UserModel.delete_collection()
    else:
        try_send_message(user_data, message)


def try_send_message(user, message):
    validate_quick_reply(user, message)

    message_content = message.get('text', '')

    if 'HELP' in message_content:
        send_loop_messages(user, 'help', 'help')
    elif 'DEVELOPER' in message_content:
        send_loop_messages(user, 'help', 'developer')


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
            lat, lng = coordinates['lat'], coordinates['long']

            set_user_location(user, lat, lng)
            check_actions(user, 'WEATHER')


def set_user_location(user, lat, lng):
    data_model = call_geosname_api(lat, lng)

    locations = user.get('locations', [])
    locations.append({
        'lat': lat,
        'lng': lng,
        'city': data_model['city']
    })
    user['locations'] = locations
    UserModel.save(user)

    send_loop_messages(user, 'specific', 'WEATHER', data_model)


def check_actions(user, action):
    actions = user.get('actions', [])
    action_done = {action: True}

    if action_done not in actions:
        actions.append(action_done)
        user['actions'] = actions
        UserModel.save(user)

        send_loop_messages(user, 'done', action)


def send_loop_messages(user, message_type='', context='', data_model=None):
    messages = MessageModel.find_by_order(type=message_type, context=context)
    for message in messages:
        # Simulate typing
        type_simulation = create_type_simulation(user)
        call_send_api(type_simulation)
        # Send message
        type_message = get_message_data(user, message, data_model)
        call_send_api(type_message)


def get_message_data(user, message, data_model):
    type_message = message['type_message']
    if type_message == 'text_message':
        return create_text_message(user, message, data_model)
    elif type_message == 'quick_reply':
        return create_quick_reply(user, message)
    elif type_message == 'quick_reply_location':
        return create_location_ask(user, message)


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


def call_geosname_api(lat, lng):
    response = requests.get('http://api.geonames.org/findNearByWeatherJSON',
                            params={'lat': lat, 'lng': lng, 'username': global_geonames_user})

    if response.status_code == 200:
        weather = json.loads(response.text)['weatherObservation']

        return {
            'city': weather['stationName'],
            'datetime': weather['datetime'],
            'temperature': weather['temperature'],
            'humidity': weather['humidity'],
            'pressure': weather['hectoPascAltimeter'],
            'elevation': weather['elevation'],
            'wind_speed': weather['windSpeed']
        }
