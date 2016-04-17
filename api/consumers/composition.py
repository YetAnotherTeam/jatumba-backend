import ujson
from channels import Group
from channels.sessions import channel_session
from django.contrib.auth import get_user_model

from api.auth.channels import token_session_user
from api.models import Composition
from api.serializers import CompositionSerializer, UserSerializer

User = get_user_model()
COMPOSITION_GROUP_TEMPLATE = 'composition-%s'


@token_session_user
@channel_session
def ws_connect(message, composition_id):
    user = message.user
    if (user.is_authenticated() and
            Composition.objects.filter(id=composition_id, band__members__user=user.id).exists()):
        message.channel_session['user'] = user.id
        Group(COMPOSITION_GROUP_TEMPLATE % composition_id).add(message.reply_channel)
        composition = Composition.objects.get(id=composition_id)
        data = CompositionSerializer(composition).data
        Group(COMPOSITION_GROUP_TEMPLATE % composition_id).send({"text": ujson.dumps(data)})
    else:
        message.reply_channel.send(
            {"text": ujson.dumps({'error': 'Вы не имеете права редактировать эту композицию'})}
        )


@channel_session
def ws_receive(message, composition_id):
    print("receive")
    user = User.objects.get(id=message.channel_session['user'])
    Group(COMPOSITION_GROUP_TEMPLATE % composition_id).send(
        {'text': ujson.dumps({
            'composition': CompositionSerializer(Composition.objects.get(id=composition_id)).data,
            'message': message.content['text'],
            'user': UserSerializer(user).data
        })}
    )


@channel_session
def ws_disconnect(message, composition_id):
    print('disconnect')
    Group(COMPOSITION_GROUP_TEMPLATE % composition_id).discard(message.reply_channel)
