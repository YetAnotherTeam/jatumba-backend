from rest_framework import serializers

from api.models import *


class BandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Band
        fields = ('id', 'name', 'description')
