import json
from channels.auth import http_session_user, channel_session_user, channel_session_user_from_http
from channels.sessions import channel_session
from channels import Group


@channel_session
def ws_connect(message):
    print('connect')
    Group('band-%d' % 123).add(message.reply_channel)
    Group('band-%d' % 123).send(
        {'text': json.dumps({'message': "123123", 'sender': message.reply_channel.name})}
    )


@http_session_user
@channel_session
def ws_receive(message):
    print("receive")
    user = message.user
    user_full_name = message.user.get_full_name() if user.is_authenticated() else 'Anonymous'
    Group('band-%d' % 123).send({'text': message.content['text'] + "- from: " + user_full_name})


@channel_session
def ws_disconnect(message):
    print('disconnect')
    Group('band-%d' % 123).discard(message.reply_channel)
