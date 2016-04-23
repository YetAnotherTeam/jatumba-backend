import ujson

from channels import Group
from django.contrib.auth import get_user_model
from rest_framework import status

from api.consumers.base import forbidden, bad_request
from api.models import Session, Composition
from api.serializers import CompositionVersionSerializer
from api.socket.serializers import SocketCompositionVersionSerializer

User = get_user_model()
COMPOSITION_GROUP_TEMPLATE = 'Composition-%s'


def check_composition_perms(data, composition_id):
    access_token = data.get('access_token')
    if access_token:
        session = Session.objects.filter(access_token=access_token).select_related('user').first()
        if session is not None:
            user = session.user
            if Composition.objects.filter(id=composition_id, band__members__user=user.id).exists():
                return user
    return None


def sign_in(message, composition_id, data):
    user = check_composition_perms(data, composition_id)
    if user is not None:
        message.channel_session['user'] = user.id
        Group(COMPOSITION_GROUP_TEMPLATE % composition_id).add(message.reply_channel)
        composition = Composition.objects.get(id=composition_id)
        message.reply_channel.send(
            {
                "text": ujson.dumps(
                    SocketCompositionVersionSerializer(
                        {
                            'method': 'sign_in',
                            'user': user.id,
                            'data': composition.versions.last(),
                            'status': status.HTTP_200_OK,
                        }
                    ).data
                )
            }
        )
    else:
        forbidden(message)


def commit(message, composition_id, data):
    if 'user' in message.channel_session:
        if isinstance(data, dict):
            data['composition'] = composition_id
            serializer = CompositionVersionSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                composition = Composition.objects.get(id=composition_id)
                (Group(COMPOSITION_GROUP_TEMPLATE % composition_id)
                    .send(
                    {
                        "text": ujson.dumps(
                            SocketCompositionVersionSerializer(
                                {
                                    # TODO временно пока не сделаем нормальный дифф
                                    'method': 'diff',
                                    'user': message.channel_session['user'],
                                    'data': composition.versions.last(),
                                    'status': status.HTTP_200_OK,
                                }
                            ).data
                        )
                    }
                ))
            else:
                message.reply_channel.send({"text": ujson.dumps(
                    {"status": 400, "data": serializer.errors}
                )})
        else:
            bad_request(message)
    else:
        forbidden(message)


def disconnect(message, composition_id):
    Group(COMPOSITION_GROUP_TEMPLATE % composition_id).discard(message.reply_channel)
