from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from api.models import Session

from .user import UserSerializer

User = get_user_model()


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ('access_token', 'refresh_token')


# noinspection PyAbstractClass
class SignInSerializer(serializers.Serializer):
    username = serializers.CharField(label='Юзернейм')
    password = serializers.CharField(style={'input_type': 'password'}, label='Пароль')


# noinspection PyAbstractClass
class IsAuthenticatedSerializer(serializers.Serializer):
    access_token = serializers.CharField()


# noinspection PyAbstractClass
class RefreshSessionSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


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
class AuthResponseSerializer(serializers.Serializer):
    user = UserSerializer(read_only=True)
    session = SessionSerializer(read_only=True)
