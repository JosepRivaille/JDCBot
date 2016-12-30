def simulate_message_typing(recipient_id):
    return {
        'recipient': {
            'id': recipient_id
        },
        'sender_action': 'typing_on'
    }


def check_message_viewed(recipient_id):
    return {
        'recipient': {
            'id': recipient_id
        },
        'sender_action': 'mark_seen'
    }


def text_message(recipient_id, message_text):
    return {
        'recipient': {
            'id': recipient_id
        },
        'message': {
            'text': message_text
        }
    }


def item_quick_reply(title, payload):
    return {
        'content_type': 'text',
        'title': title,
        'payload': payload
    }


def quick_reply(recipient_id, title, quick_replies):
    return {
        'recipient': {
            'id': recipient_id
        },
        'message': {
            'text': title,
            'quick_replies': quick_replies
        }
    }


def quick_reply_location(recipient_id, title):
    return {
        'recipient': {
            'id': recipient_id
        },
        'message': {
            'text': title,
            'quick_replies': [
                {
                    'content_type': 'location'
                }
            ]
        }
    }


def template_message_generic(recipient_id, elements):
    return {
        'recipient': {
            'id': recipient_id
        },
        'message': {
            'attachment': {
                'type': 'template',
                'payload': {
                    'template_type': 'generic',
                    'elements': elements
                }
            }
        }
    }


def multimedia_message(recipient_id, url, type_message):
    return {
        'recipient': {
            'id': recipient_id
        },
        'message': {
            'attachment': {
                'type': type_message,
                'payload': {
                    'url': url
                }
            }
        }
    }


def image_message(recipient_id, url):
    return multimedia_message(recipient_id, url, 'image')


def video_message(recipient_id, url):
    return multimedia_message(recipient_id, url, 'video')


def audio_message(recipient_id, url):
    return multimedia_message(recipient_id, url, 'audio')


def file_message(recipient_id, url):
    return multimedia_message(recipient_id, url, 'file')
