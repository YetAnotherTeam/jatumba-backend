from rest_framework import serializers

from api.models import *


# noinspection PyAbstractClass
class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'first_name', 'last_name')


# noinspection PyAbstractClass
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'phone', 'vk_profile', 'fb_profile')


# noinspection PyAbstractClass
class SessionSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Session
        fields = ('access_token', 'refresh_token', 'user')


# noinspection PyAbstractClass
class BandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Band
