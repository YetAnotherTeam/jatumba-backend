import ujson

NOT_FOUND_MESSAGE = 'Path not found.'
BAD_REQUEST = 'Bad request'
UNAUTHORIZED = 'Unauthorized'

def not_found(message):
    message.reply_channel.send({"text": ujson.dumps({'code': 404, 'data': NOT_FOUND_MESSAGE})})


def pass_message(*args, **kwargs):
    pass


def bad_request(message):
    message.reply_channel.send({"text": ujson.dumps({'code': 400, 'data': BAD_REQUEST})})


def unauthorized(message):
    message.reply_channel.send({"text": ujson.dumps({'code': 401, 'data': UNAUTHORIZED})})
