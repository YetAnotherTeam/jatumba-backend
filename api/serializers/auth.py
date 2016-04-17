from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.models import Session

User = get_user_model()


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'first_name', 'last_name')


# noinspection PyAbstractClass
class SignInSerializer(serializers.Serializer):
    username = serializers.CharField(label='Юзернейм')
    password = serializers.CharField(style={'input_type': 'password'}, label='Пароль')


# noinspection PyAbstractClass
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'phone', 'vk_profile', 'fb_profile')
        extra_kwargs = {'vk_profile': {'read_only': True}, 'fb_profile': {'read_only': True}}


# noinspection PyAbstractClass
class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ('access_token', 'refresh_token')


# noinspection PyAbstractClass
class AuthResponseSerializer(serializers.Serializer):
    user = UserSerializer()
    session = SessionSerializer()
