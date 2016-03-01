from rest_framework import serializers

from api.models import *


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'first_name', 'last_name')

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        Profile.objects.create(user=user)
        return user


class UserSerializer(serializers.ModelSerializer):
    phone = serializers.SerializerMethodField()
    vk_profile = serializers.SerializerMethodField()
    fb_profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'phone', 'vk_profile', 'fb_profile')

    def get_phone(self, user):
        profile = user.profile
        if profile:
            return profile.phone
        else:
            return ''

    def get_vk_profile(self, user):
        profile = user.profile
        if profile.vk_profile:
            return 'http://vk.com/%s' % profile.vk_profile
        else:
            return ''

    def get_fb_profile(self, user):
        profile = user.profile
        if profile.fb_profile:
            return 'http://facebook.com/%s' % profile.fb_profile
        else:
            return ''


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('public_username', 'phone')


class SessionSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Session
        fields = ('access_token', 'refresh_token', 'user')


class BandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Band