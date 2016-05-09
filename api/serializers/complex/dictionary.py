# noinspection PyAbstractClass
from rest_framework import serializers

from api.models import Instrument
from api.serializers.elementary.dictionary import SoundSerializer
from utils.django_rest_framework.serializers import DynamicFieldsMixin


class InstrumentListItemSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    sounds = SoundSerializer(many=True)

    class Meta:
        model = Instrument
        fields = ('id', 'name', 'sounds')
