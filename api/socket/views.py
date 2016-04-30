from channels import Group
from rest_framework import status

from api.consumers.base import bad_request, forbidden
from api.models import Session, Composition
from api.serializers import CompositionVersionSerializer
from api.socket.serializers import SocketCompositionVersionSerializer
from rest_channels.views import SocketView


class CompositionSocketView(SocketView):
    COMPOSITION_GROUP_TEMPLATE = 'Composition-%s'

    def receive(self, request, *args, **kwargs):
        request_data = request.data
        method = request_data.get('method')
        composition_id = kwargs.get('composition_id')
        data = request_data.get('data')
        if method == 'sign_in':
            self.sign_in(request, composition_id, data)
        elif method == 'diff':
            self.commit(request, composition_id, data)
        elif method == 'history_back':
            pass
        elif method == 'history_forward':
            pass
        elif method == 'commit':
            self.commit(request, composition_id, data)
        else:
            bad_request(request)

    def disconnect(self, request, *args, **kwargs):
        composition_id = kwargs.get('composition_id')
        Group(self.COMPOSITION_GROUP_TEMPLATE % composition_id).discard(request.reply_channel)

    def check_composition_perms(self, data, composition_id):
        access_token = data.get('access_token')
        if access_token:
            session = Session.objects.filter(access_token=access_token).select_related(
                'user').first()
            if session is not None:
                user = session.user
                if (Composition
                        .objects
                        .filter(id=composition_id, band__members__user=user.id)
                        .exists()):
                    return user
        return None

    def sign_in(self, message, composition_id, data):
        user = self.check_composition_perms(data, composition_id)
        if user is not None:
            message.channel_session['user'] = user.id
            Group(self.COMPOSITION_GROUP_TEMPLATE % composition_id).add(message.reply_channel)
            composition = Composition.objects.get(id=composition_id)
            self.send(
                message.reply_channel,
                SocketCompositionVersionSerializer(
                    {
                        'method': 'sign_in',
                        'user': user.id,
                        'data': composition.versions.last(),
                        'status': status.HTTP_200_OK,
                    }
                ).data
            )

        else:
            forbidden(message)

    def commit(self, message, composition_id, data):
        if 'user' in message.channel_session:
            if isinstance(data, dict):
                data['composition'] = composition_id
                serializer = CompositionVersionSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                    composition = Composition.objects.get(id=composition_id)
                    self.send(
                        Group(self.COMPOSITION_GROUP_TEMPLATE % composition_id),
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
                else:
                    self.send(message.reply_channel, {"status": 400, "data": serializer.errors})
            else:
                bad_request(message)
        else:
            forbidden(message)
