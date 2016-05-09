import time

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.auth.authentication import TokenAuthentication
from api.models import Session
from api.serializers.elementary.auth import UserSerializer, SessionSerializer

User = get_user_model()


class SignUpSerializer(UserSerializer):
    required_fields = ('username', 'password', 'first_name', 'last_name', 'avatar')

    class Meta(UserSerializer.Meta):
        extra_kwargs = {
            'vk_profile': {'read_only': True},
            'fb_profile': {'read_only': True}
        }

    def create(self, validated_data):
        if validated_data.get('password'):
            validated_data['password'] = make_password(
                validated_data['password']
            )
        return super(SignUpSerializer, self).create(validated_data)


# noinspection PyAbstractClass
class SignInSerializer(serializers.Serializer):
    username = serializers.CharField(label='Юзернейм')
    password = serializers.CharField(style={'input_type': 'password'}, label='Пароль')


# noinspection PyAbstractClass
class SignInSocketSerializer(serializers.Serializer):
    access_token = serializers.CharField()


# noinspection PyAbstractClass
class IsAuthenticatedSerializer(serializers.Serializer):
    access_token = serializers.CharField()

    def validate_access_token(self, access_token):
        session = Session.objects.filter(access_token=access_token).first()
        if (session is None or
                (time.time() - session.time > TokenAuthentication.SESSION_EXPIRE_TIME)):
            raise ValidationError('access token not valid or expired')
        return access_token


# noinspection PyAbstractClass
class AuthResponseSerializer(serializers.Serializer):
    user = UserSerializer()
    session = SessionSerializer()
