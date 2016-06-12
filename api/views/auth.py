import binascii
import os
import time

import requests
from django.contrib.auth import authenticate, get_user_model
from django.core.files.base import ContentFile
from django.db.transaction import atomic
from rest_framework import filters, mixins, status, views, viewsets
from rest_framework.decorators import list_route
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny, DjangoObjectPermissions
from rest_framework.response import Response

from api.auth.auth_providers.fb_api import FB
from api.auth.auth_providers.vk_api import VK
from api.auth.authentication import TokenAuthentication
from api.auth.session_generator import generate_session_params
from api.models import Session
from api.serializers import (
    AuthResponseSerializer, IsAuthenticatedSerializer, RefreshSessionSerializer, SignInSerializer,
    SignUpSerializer, UserRetrieveSerializer, UserSerializer
)

User = get_user_model()


@atomic
def social_auth(user_data, request):
    username = request.data.get('username')
    if username is None or username == '':
        return Response(
            {'error': 'User not found, register new by including username in request.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    user = User.objects.filter(username=username).first()
    if user:
        return Response({'error': 'username already taken'}, status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.create_user(
        username,
        password=binascii.hexlify(os.urandom(10)).decode('utf-8'),
        first_name=user_data['first_name'],
        last_name=user_data['last_name']
    )

    if user_data['network'] is 'fb':
        user.fb_profile = user_data['user_id']
    elif user_data['network'] is 'vk':
        user.vk_profile = user_data['user_id']
        url = user_data['photo_max_orig']
        response = requests.get(url)
        user.avatar.save(os.path.basename(url), ContentFile(response.content), save=False)
    user.save()
    return Response(AuthResponseSerializer(generate_auth_response(user)).data)


class SocialAuthView(views.APIView):
    user_profile_field = None
    social_backend = None

    def __init__(self, **kwargs):
        assert self.social_backend is not None, \
            "SocialAuthView must provide a `social_backend` field"
        assert self.user_profile_field is not None, \
            "SocialAuthView must provide a `user_profile_field` field"
        super(SocialAuthView, self).__init__(**kwargs)

    def post(self, request):
        token = request.data.get('token')
        user_data = self.social_backend.get_user_data(token)
        user = User.objects.filter(**{self.user_profile_field: user_data['user_id']}).first()
        if user:
            return Response(AuthResponseSerializer(generate_auth_response(user)).data)
        else:
            return social_auth(user_data, request)


class VKAuthView(SocialAuthView):
    permission_classes = ()
    user_profile_field = 'vk_profile'
    social_backend = VK()


class FBAuthView(SocialAuthView):
    permission_classes = ()
    user_profile_field = 'fb_profile'
    social_backend = FB()


def generate_auth_response(user):
    return {
        'user': user,
        'session': Session.objects.create(**generate_session_params(user)),
    }


class SessionViewSet(viewsets.GenericViewSet):
    queryset = Session.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RefreshSessionSerializer

    @list_route(methods=['post'])
    def refresh(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        old_session = Session.objects.filter(refresh_token=serializer.data['refresh_token']).first()
        if old_session is None:
            raise ValidationError('Invalid token.')
        new_session = generate_auth_response(old_session.user)
        old_session.delete()
        return Response(AuthResponseSerializer(new_session).data)


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    querysets = {
        'DEFAULT': User.objects.all(),
        'retrieve': User.objects.prefetch_related('members__band'),
    }
    permission_classes = (DjangoObjectPermissions,)
    queryset = User.objects.all()
    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter,)
    filter_fields = ('members__band',)
    search_fields = ('id', 'username', 'first_name', 'last_name')
    serializers = {
        'DEFAULT': UserSerializer,
        'retrieve': UserRetrieveSerializer,
        'sign_up': SignUpSerializer,
        'sign_in': SignInSerializer,
        'is_authenticated': IsAuthenticatedSerializer,
    }

    def get_queryset(self):
        return self.querysets.get(self.action, self.querysets['DEFAULT'])

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.serializers['DEFAULT'])

    @list_route(methods=['post'], permission_classes=(AllowAny,),
                parser_classes=(MultiPartParser,))
    def sign_up(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            AuthResponseSerializer(instance=generate_auth_response(user)).data,
            status=status.HTTP_201_CREATED
        )

    @list_route(methods=['post'], permission_classes=(AllowAny,))
    def sign_in(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(**serializer.data)
        if user:
            user.sessions.all().delete()
            return Response(AuthResponseSerializer(instance=generate_auth_response(user)).data)
        else:
            return Response(
                {'error': 'Wrong username or password'},
                status=status.HTTP_403_FORBIDDEN
            )

    @list_route(methods=['post'], permission_classes=(AllowAny,))
    def is_authenticated(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        access_token = serializer.data['access_token']
        session = Session.objects.filter(access_token=access_token).first()
        if (session is None or
                (time.time() - session.time > TokenAuthentication.SESSION_EXPIRE_TIME)):
            raise AuthenticationFailed('Access token not valid or expired.')
        return Response(AuthResponseSerializer({'user': session.user, 'session': session}).data)
