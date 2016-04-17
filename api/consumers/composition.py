import ujson
from channels.sessions import channel_session

from api.consumers.handlers.composition import sign_in, disconnect, diff, commit


@channel_session
def ws_receive(message, composition_id):
    message_text = message.content['text']
    request_json = ujson.loads(message_text)
    method = request_json.get('method')
    data = request_json.get('data')
    if method == 'sign_in':
        sign_in(message, composition_id, data)
    elif method == 'diff':
        diff(message, composition_id)
    elif method == 'commit':
        commit(message, composition_id)


@channel_session
def ws_disconnect(message, composition_id):
    disconnect(message, composition_id)
