import ujson

NOT_FOUND_MESSAGE = 'Такой путь не найден.'


def not_found(message):
    message.reply_channel.send({"text": ujson.dumps({'error': NOT_FOUND_MESSAGE})})


def pass_message(*args, **kwargs):
    pass
