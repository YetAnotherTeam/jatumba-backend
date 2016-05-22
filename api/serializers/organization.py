from rest_framework import serializers

from api.models import *
from .auth.user import UserSerializer
from utils.django_rest_framework.fields import SerializableRelatedField
from utils.django_rest_framework.serializers import DynamicFieldsMixin


class BandSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    user_joined = serializers.SerializerMethodField()

    class Meta:
        model = Band
        fields = ('id', 'name', 'description', 'user_joined')

    def get_user_joined(self, band):
        return band.members.filter(user=self.context['request'].user).exists()


class MemberSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    user = SerializableRelatedField(serializer=UserSerializer)
    band = SerializableRelatedField(
        serializer=BandSerializer,
        serializer_params={'required_fields': ('id', 'name', 'description')}
    )

    class Meta:
        model = Member
        fields = ('id', 'user', 'band')
