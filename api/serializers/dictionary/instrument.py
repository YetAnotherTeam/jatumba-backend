from rest_framework import serializers

from api.models import Instrument

from .sound import SoundSerializer


class InstrumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instrument
        fields = '__all__'


class InstrumentListItemSerializer(serializers.ModelSerializer):
    sounds = SoundSerializer(many=True)

    class Meta:
        model = Instrument
        fields = ('id', 'name', 'sounds')
