import ujson
from channels import Group
from django.contrib.auth import get_user_model

from api.models import Session, Composition
from api.serializers import CompositionSerializer

User = get_user_model()
COMPOSITION_GROUP_TEMPLATE = 'composition-%s'


def check_composition_perms(message, composition_id):
    access_token = message.content.get('access_token')
    if access_token:
        session = Session.objects.filter(access_token=access_token).select_related('user').first()
        if session is not None:
            user = session.user
            if Composition.objects.filter(id=composition_id, band__members__user=user.id).exists():
                return user
    return None


def sign_in(message, composition_id):
    check_composition_perms(message, composition_id)
    user = check_composition_perms(message, composition_id)
    if user is not None:
        message.channel_session['user'] = user.id
        Group(COMPOSITION_GROUP_TEMPLATE % composition_id).add(message.reply_channel)
        composition = Composition.objects.get(id=composition_id)
        (Group(COMPOSITION_GROUP_TEMPLATE % composition_id)
            .send({"text": ujson.dumps(CompositionSerializer(composition).data)}))


def diff(message, composition_id):
    initial_data = message.content.get('composition')


def commit(messge, composition_id):
    pass


def disconnect(message, composition_id):
    Group(COMPOSITION_GROUP_TEMPLATE % composition_id).discard(message.reply_channel)