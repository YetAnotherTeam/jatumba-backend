import ujson

from rest_framework import status

BAD_REQUEST = 'Bad request'
UNAUTHORIZED = 'Unauthorized'
NOT_FOUND = 'Path not found.'


def pass_message(*args, **kwargs):
    pass


def bad_request(message):
    message.reply_channel.send(
        {"text": ujson.dumps({'code': status.HTTP_400_BAD_REQUEST, 'data': BAD_REQUEST})}
    )


def unauthorized(message):
    message.reply_channel.send(
        {"text": ujson.dumps({'code': status.HTTP_401_UNAUTHORIZED, 'data': UNAUTHORIZED})}
    )


def not_found(message):
    message.reply_channel.send(
        {"text": ujson.dumps({'code': status.HTTP_404_NOT_FOUND, 'data': NOT_FOUND})}
    )
