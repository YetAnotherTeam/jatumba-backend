import ujson
from channels.sessions import channel_session

from api.consumers.base import bad_request
from api.consumers.handlers.composition import sign_in, disconnect, commit


@channel_session
def ws_receive(message, composition_id):
    message_text = message.content['text']
    # try:
    request_json = ujson.loads(message_text)
    if isinstance(request_json, dict):
        method = request_json.get('method')
        data = request_json.get('data')
        if method == 'sign_in':
            sign_in(message, composition_id, data)
        elif method == 'diff':
            commit(message, composition_id, data)
        elif method == 'history_back':
            pass
        elif method == 'history_forward':
            pass
        elif method == 'commit':
            commit(message, composition_id, data)
        else:
            bad_request(message)
    else:
        bad_request(message)
    # except ValueError as e:
    #     print(e)
    #     bad_request(message)



@channel_session
def ws_disconnect(message, composition_id):
    disconnect(message, composition_id)
