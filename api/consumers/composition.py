import ujson
from channels.sessions import channel_session



@channel_session
def ws_receive(message, composition_id):
    message_text = message.content['text']
    request_json = None
    try:
        request_json = ujson.loads(message_text)
    except ValueError as e:
        print(e)
