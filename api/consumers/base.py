import ujson

NOT_FOUND_MESSAGE = 'Path not found.'


def not_found(message):
    message.reply_channel.send({"text": ujson.dumps({'error': NOT_FOUND_MESSAGE})})


def pass_message(*args, **kwargs):
    pass
