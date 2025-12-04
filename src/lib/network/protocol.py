def format_message(msg_code, content):
    return {
        'type': msg_code,
        'content': content
    }

def parse_message(message):
    return message['type'], message['content']

MSG_CODE_GAMESTATE = 0
MSG_CODE_POSITION = 1
MSG_CODE_LOAD = 2
MSG_CODE_ADD_MISSILE = 3