from flask import Flask
from flask import request

from config import DevelopmentConfig
from handler import receive_message

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)


@app.route('/webHook', methods=['GET', 'POST'])
def web_hook():
    if request.method == 'GET':
        verify_token = request.args.get('hub.verify_token', '')
        if verify_token == app.config['SECRET_KEY']:
            return request.args.get('hub.challenge', '')
        return 'Error validating token'

    elif request.method == 'POST':
        payload = request.get_json()

        for entry in payload['entry']:
            for message_event in entry['messaging']:
                if 'message' in message_event:
                    receive_message(message_event, app.config['PAGE_ACCESS_TOKEN'])

        return 'OK'


@app.route('/', methods=['GET'])
def index():
    return 'Hello to bot course'


if __name__ == '__main__':
    app.run(port=8000)
