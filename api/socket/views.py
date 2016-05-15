from channels import Group
from django.contrib.auth import get_user_model
from django.db.transaction import atomic
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ValidationError, NotFound

from api.models import (
    Session, Composition, Band, Message, DiffCompositionVersion, CompositionVersion
)
from api.serializers import (
    CompositionVersionSerializer, MessagesSerializer, IsAuthenticatedSerializer,
    DiffCompositionVersionSerializer, DiffHistorySerializer, MessageCreateSerializer
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
        serializer = IsAuthenticatedSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        composition_id = kwargs.get('composition_id')
        user = self.check_composition_perms(serializer, composition_id)
        if user is not None:
            request.channel_session['user'] = user.id
            Group(self.COMPOSITION_GROUP_TEMPLATE % composition_id).add(request.reply_channel)
            composition = Composition.objects.get(id=composition_id)
            diff_version = composition.diff_versions.last()
            if diff_version is None:
                composition_version = composition.versions.last()
                diff_version = DiffCompositionVersion.copy_from_version(composition_version)
            self.route_send(
                request.reply_channel,
                DiffCompositionVersionSerializer(diff_version).data
            )
        else:
            raise PermissionDenied

    @socket_route
    def diff(self, request, data, *args, **kwargs):
        if 'user' in request.channel_session:
            composition_id = kwargs.get('composition_id')
            data['composition'] = composition_id
            serializer = DiffCompositionVersionSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            self.route_send(
                Group(self.COMPOSITION_GROUP_TEMPLATE % composition_id),
                serializer.data,
                status.HTTP_201_CREATED
            )
        else:
            raise PermissionDenied

    @socket_route
    def commit(self, request, data, *args, **kwargs):
        user_id = request.channel_session.get('user')
        if user_id is not None:
            composition_id = kwargs.get('composition_id')
            data['composition'] = composition_id
            if (DiffCompositionVersion.objects
                    .filter(composition_id=composition_id)
                    .count() <= 1):
                raise ValidationError('Nothing to commit.')
            diff_version = (DiffCompositionVersion.objects
                            .filter(composition_id=composition_id)
                            .last())
            composition_version = self.perform_commit(diff_version, user_id)
            self.route_send(
                Group(self.COMPOSITION_GROUP_TEMPLATE % composition_id),
                CompositionVersionSerializer(composition_version).data,
                status.HTTP_201_CREATED
            )
        else:
            raise PermissionDenied

    def history(self, request, data, error_message, filter_lookup, order_function, *args, **kwargs):
        user_id = request.channel_session.get('user')
        if user_id is not None:
            composition_id = int(kwargs.get('composition_id'))
            serializer = DiffHistorySerializer(
                data=data,
                context={'composition_id': composition_id}
            )
            serializer.is_valid(raise_exception=True)
            diff_version_id = serializer.data['diff_composition_version']
            diff_version = getattr(DiffCompositionVersion.objects
                                   .filter(
                                        composition_id=composition_id,
                                        **{filter_lookup: diff_version_id}
                                    ), order_function)()
            if diff_version is None:
                raise NotFound(error_message)
            self.route_send(
                request.reply_channel,
                DiffCompositionVersionSerializer(diff_version).data,
                status.HTTP_200_OK
            )
        else:
            raise PermissionDenied

    @socket_route
    def history_up(self, request, data, *args, **kwargs):
        self.history(request, data, 'You have come to the beginning.', 'id__lt', 'last', *args,
                     **kwargs)

    @socket_route
    def history_down(self, request, data, *args, **kwargs):
        self.history(request, data, 'You have come to the end.', 'id__gt', 'first', *args,
                     **kwargs)

    @atomic
    def perform_commit(self, diff_version, user_id):
        version = CompositionVersion.copy_from_diff_version(diff_version, user_id)
        (DiffCompositionVersion.objects
         .filter(composition_id=diff_version.composition_id)
         .delete())
        return version


class ChatSocketView(SocketRouteView):
    CHAT_GROUP_TEMPLATE = 'Chat-%s'
    MESSAGES_COUNT = 20

    def disconnect(self, request, *args, **kwargs):
        band_id = kwargs.get('band_id')
        group = Group(self.CHAT_GROUP_TEMPLATE % band_id)
        group.discard(request.reply_channel)
        # self.send(group, {'leave': UserSerializer(user.id)})

    def check_chat_perms(self, serializer, band_id):
        session = (Session
                   .objects
                   .filter(access_token=serializer.data['access_token'])
                   .select_related('user')
                   .first())
        if session is not None:
            user = session.user
            if (Band
                    .objects
                    .filter(id=band_id, members__user=user.id)
                    .exists()):
                return user
        return None

    @socket_route
    def sign_in(self, request, data, *args, **kwargs):
        serializer = IsAuthenticatedSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        band_id = kwargs.get('band_id')
        user = self.check_chat_perms(serializer, band_id)
        if user is not None:
            request.channel_session['user'] = user.id
            group = Group(self.CHAT_GROUP_TEMPLATE % band_id)
            group.add(request.reply_channel)
            messages = Message.objects.all()[:self.MESSAGES_COUNT][::-1]
            self.route_send(
                request.reply_channel,
                MessagesSerializer({"messages": messages}).data
            )
        else:
            raise PermissionDenied

    @socket_route
    def publish(self, request, data, *args, **kwargs):
        if 'user' in request.channel_session:
            band_id = kwargs.get('band_id')
            serializer = MessageCreateSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save(
                author=User.objects.get(pk=request.channel_session['user']),
                band=Band.objects.get(pk=band_id)
            )
            group = Group(self.CHAT_GROUP_TEMPLATE % band_id)
            self.route_send(
                group,
                serializer.data
            )
        else:
            raise PermissionDenied

    @socket_route
    def list(self, request, data, *args, **kwargs):
        if 'user' in request.channel_session:
            # TODO возможно стоит добавить просмотр сообщений до последних 20
            pass
        else:
            raise PermissionDenied
