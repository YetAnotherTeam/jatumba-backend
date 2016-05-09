from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.models import Session
from utils.django_rest_framework.serializers import DynamicFieldsMixin

User = get_user_model()


class UserSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'password', 'phone', 'vk_profile',
                  'fb_profile', 'avatar')
        extra_kwargs = {
            'vk_profile': {'read_only': True},
            'fb_profile': {'read_only': True},
            'password': {'write_only': True}
        }


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ('access_token', 'refresh_token')