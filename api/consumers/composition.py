from channels.sessions import channel_session

from api.consumers.handlers.composition import sign_in, disconnect, diff, commit


@channel_session
def ws_receive(message, composition_id):
    method = message.content.get('method')
    if method == 'sign_in':
        sign_in(message, composition_id)
    elif method == 'diff':
        diff(message, composition_id)
    elif method == 'commit':
        commit(message, composition_id)


@channel_session
def ws_disconnect(message, composition_id):
    disconnect(message, composition_id)
