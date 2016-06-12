from rest_framework import serializers

from api.models import Band
from utils.django_rest_framework.serializers import DynamicFieldsMixin


class BandSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    user_joined = serializers.SerializerMethodField()

    class Meta:
        model = Band
        fields = ('id', 'name', 'description', 'user_joined')

    def get_user_joined(self, band):
        return bool(band.user_joined)
