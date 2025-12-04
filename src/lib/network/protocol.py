def format_message(msg_code, content):
    return {
        'type': msg_code,
        'content': content
    }

def parse_message(message):
    return message['type'], message['content']

MSG_CODE_MAP = 0
MSG_CODE_PLAYER = 1
MSG_CODE_KILL = 2