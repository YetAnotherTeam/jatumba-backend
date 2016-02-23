from api import models
from django.contrib.auth.models import User
from rest_framework import serializers

from api.models import Profile


class UserSerializer(serializers.ModelSerializer):
    public_username = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'public_username', 'phone')

    def get_public_username(self, obj):
        return Profile.objects.filter(user=obj).first().public_username

    def get_phone(self, obj):
        return Profile.objects.filter(user=obj).first().phone


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        models = models.Profile
        fields = ('public_username', 'phone')


class SessionSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = models.Session
        fields = ('access_token', 'refresh_token', 'user')
