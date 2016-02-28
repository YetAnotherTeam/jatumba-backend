from django.contrib.auth.models import User
from rest_framework import serializers

from api import models


class UserSerializer(serializers.ModelSerializer):
    phone = serializers.SerializerMethodField()
    vk_profile = serializers.SerializerMethodField()
    fb_profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'phone', 'vk_profile', 'fb_profile')

    def get_phone(self, obj):
        profile = models.Profile.objects.filter(user=obj).first()
        if profile:
            return profile.phone
        else:
            return ''

    def get_vk_profile(self, obj):
        profile = models.Profile.objects.filter(user=obj).first()
        if profile:
            return 'http://vk.com/' + profile.vk_profile
        else:
            return ''

    def get_fb_profile(self, obj):
        profile = models.Profile.objects.filter(user=obj).first()
        if profile:
            return 'http://facebook.com/' + profile.vk_profile
        else:
            return ''


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        models = models.Profile
        fields = ('public_username', 'phone')


class SessionSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = models.Session
        fields = ('access_token', 'refresh_token', 'user')
