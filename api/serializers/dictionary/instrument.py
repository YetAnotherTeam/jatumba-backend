from rest_framework import serializers

from api.models import Instrument
from utils.django_rest_framework.serializers import DynamicFieldsMixin

from .sound import SoundSerializer


class InstrumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instrument
        fields = '__all__'


class InstrumentListItemSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    sounds = SoundSerializer(many=True)

    class Meta:
        model = Instrument
        fields = ('id', 'name', 'sounds')
