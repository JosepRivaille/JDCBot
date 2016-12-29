import requests
import json


def call_send_api(data, token):
    response = requests.post('https://graph.facebook.com/v2.6/me/messages',
                             params={'access_token': token},
                             data=json.dumps(data),
                             headers={'Content-type': 'application/json'})
    if response.status_code == 200:
        print('Message sent successfully')
    else:
        print(response.text)


def call_user_api(user_id, token):
    response = requests.get('https://graph.facebook.com/v2.6/' + user_id,
                            params={'access_token': token})

    if response.status_code == 200:
        return json.loads(response.text)
    else:
        print(response)


def get_started_data():
    return {
        'setting_type': 'call_to_actions',
        'thread_state': 'new_thread',
        'call_to_actions': [
            {'payload': 'START_CHAT'}
        ]
    }


def call_set_started_button_api(token):
    response = requests.post('https://graph.facebook.com/v2.6/me/thread_settings',
                             params={'access_token': token},
                             data=json.dumps(get_started_data()),
                             headers={'Content-type': 'application/json'})

    if response.status_code == 200:
        print(json.loads(response.text))


def call_delete_started_button_api(token):
    response = requests.delete('https://graph.facebook.com/v2.6/me/thread_settings',
                               params={'access_token': token},
                               data=json.dumps(get_started_data()),
                               headers={'Content-type': 'application/json'})

    if response.status_code == 200:
        print(json.loads(response.text))


def call_geosname_api(lat, lng, username):
    response = requests.get('http://api.geonames.org/findNearByWeatherJSON',
                            params={'lat': lat, 'lng': lng, 'username': username})

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
    else:
        print(response)
