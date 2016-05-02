from channels import Group
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.exceptions import PermissionDenied

from api.models import Session, Composition
from api.serializers import CompositionVersionSerializer
from api.socket.serializers import (
    SignInSocketSerializer, CompositionVersionResponseSocketSerializer
)
from rest_channels.socket_routing.decorators import socket_route
from rest_channels.socket_routing.route_views import SocketRouteView

User = get_user_model()


class CompositionSocketView(SocketRouteView):
    COMPOSITION_GROUP_TEMPLATE = 'Composition-%s'

    def disconnect(self, request, *args, **kwargs):
        composition_id = kwargs.get('composition_id')
        Group(self.COMPOSITION_GROUP_TEMPLATE % composition_id).discard(request.reply_channel)

    def check_composition_perms(self, serializer, composition_id):
        session = (Session
                   .objects
                   .filter(access_token=serializer.data['access_token'])
                   .select_related('user')
                   .first())
        if session is not None:
            user = session.user
            if (Composition
                    .objects
                    .filter(id=composition_id, band__members__user=user.id)
                    .exists()):
                return user
        return None

    @socket_route
    def sign_in(self, request, data, *args, **kwargs):
        serializer = SignInSocketSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        composition_id = kwargs.get('composition_id')
        user = self.check_composition_perms(serializer, composition_id)
        if user is not None:
            request.channel_session['user'] = user.id
            Group(self.COMPOSITION_GROUP_TEMPLATE % composition_id).add(request.reply_channel)
            composition = Composition.objects.get(id=composition_id)
            self.send(
                request.reply_channel,
                CompositionVersionResponseSocketSerializer(
                    {
                        'method': 'sign_in',
                        'user': user,
                        'data': composition.versions.last(),
                        'status': status.HTTP_200_OK,
                    }
                ).data
            )

        else:
            raise PermissionDenied

    @socket_route
    def commit(self, request, data, *args, **kwargs):
        composition_id = kwargs.get('composition_id')
        if 'user' in request.channel_session:
            data['composition'] = composition_id
            serializer = CompositionVersionSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            composition = Composition.objects.get(id=composition_id)
            self.send(
                Group(self.COMPOSITION_GROUP_TEMPLATE % composition_id),
                CompositionVersionResponseSocketSerializer(
                    {
                        # TODO временно пока не сделаем нормальный дифф
                        'method': 'diff',
                        'user': User.objects.get(pk=request.channel_session['user']),
                        'data': composition.versions.last(),
                        'status': status.HTTP_200_OK,
                    }
                ).data
            )
        else:
            raise PermissionDenied
