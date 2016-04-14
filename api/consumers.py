import json

from channels.sessions import channel_session
from channels import Group


@channel_session
def ws_connect(message):
    print('connect')
    Group('band-%d' % 123).add(message.reply_channel)
    Group('band-%d' % 123).send(
        {'text': json.dumps({'message': "123123", 'sender': message.reply_channel.name})}
    )


@channel_session
def ws_receive(message):
    print("receive")
    Group('band-%d' % 123).send({'text': message.content['text'] + "123"})


@channel_session
def ws_disconnect(message):
    print('disconnect')
    Group('band-%d' % 123).discard(message.reply_channel)
