from rest_framework import serializers

from api.models import Sound


class SoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sound
        fields = ('id', 'name', 'file')
