from rest_framework import serializers

from api.models import Band
from utils.django_rest_framework.serializers import DynamicFieldsMixin


class BandSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    user_joined = serializers.SerializerMethodField()
    is_leader = serializers.SerializerMethodField()
    compositions_count = serializers.SerializerMethodField()
    members_count = serializers.SerializerMethodField()

    class Meta:
        model = Band
        fields = (
            'id', 'name', 'description', 'user_joined', 'is_leader', 'create_datetime',
            'members_count', 'compositions_count'
        )

    def get_user_joined(self, band):
        return bool(getattr(band, 'user_joined', True))

    def get_compositions_count(self, band):
        return getattr(band, 'compositions_count', 0)

    def get_members_count(self, band):
        return getattr(band, 'members_count', 0)

    def get_is_leader(self, band):
        return band.leader.member.user_id == self.context['request'].user.id
