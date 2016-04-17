# noinspection PyAbstractClass
from rest_framework import serializers

from api.models import Instrument, Sound
from utils.django_rest_framework.serializers import DynamicFieldsMixin


class SoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sound
        fields = ('id', 'name', 'file')


class InstrumentSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    sounds = SoundSerializer(many=True)

    class Meta:
        model = Instrument
        fields = ('id', 'name', 'sounds')
