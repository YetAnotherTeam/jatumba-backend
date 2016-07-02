from rest_framework import serializers

from api.models import Band
from utils.django_rest_framework.serializers import DynamicFieldsMixin


class BandSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    user_joined = serializers.SerializerMethodField()
    is_leader = serializers.SerializerMethodField()

    class Meta:
        model = Band
        fields = ('id', 'name', 'description', 'user_joined', 'is_leader')

    def get_user_joined(self, band):
        return bool(getattr(band, 'user_joined', True))

    def get_is_leader(self, band):
        return band.lead_members.filter(user=self.context['request'].user).exists()
