def simulate_message_typing(recipient_id):
    return {
        'recipient': {'id': recipient_id},
        'sender_action': 'typing_on'
    }


def text_message(recipient_id, message_text):
    return {
        'recipient': {'id': recipient_id},
        'message': {'text': message_text}
    }


def item_quick_reply(title, payload):
    return {
        'content_type': 'text',
        'title': title,
        'payload': payload
    }


def quick_reply(recipient_id, title, quick_replies):
    return {
        'recipient': {'id': recipient_id},
        'message': {
            'text': title,
            'quick_replies': quick_replies
        }
    }