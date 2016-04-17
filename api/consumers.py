import ujson
from channels import Group
from channels.sessions import channel_session

from api.auth.channels import token_session_user
from api.models import Composition
from api.serializers import CompositionSerializer

COMPOSITION_GROUP_TEMPLATE = 'composition-%d'


@token_session_user
def ws_connect(message, composition_id):
    user = message.user
    if Composition.objects.filter(id=composition_id, band__members__user=user).exists():
        Group(COMPOSITION_GROUP_TEMPLATE % composition_id).add(message.reply_channel)
        composition = Composition.objects.get(id=composition_id)
        data = CompositionSerializer(composition).data
        Group(COMPOSITION_GROUP_TEMPLATE % composition_id).send({"text": ujson.dumps(data)})


@token_session_user
def ws_receive(message, composition_id):
    print("receive")
    user = message.user
    user_full_name = message.user.get_full_name() if user.is_authenticated() else 'Anonymous'
    Group(COMPOSITION_GROUP_TEMPLATE % composition_id).send(
        {'text': message.content['text'] + "- from: " + user_full_name})


@channel_session
def ws_disconnect(message, composition_id):
    print('disconnect')
    Group('composition-%s' % composition_id).discard(message.reply_channel)
