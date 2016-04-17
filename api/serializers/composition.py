# noinspection PyAbstractClass
from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.models import Composition, Instrument, Track, TrackHistory
from api.serializers.auth import UserSerializer
from api.serializers.dictionary import InstrumentSerializer
from utils.django_rest_framework.fields import SerializableRelatedField

User = get_user_model()


class CompositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Composition


# noinspection PyAbstractClass
class TrackSerializer(serializers.ModelSerializer):
    class NestedInstrumentSerializer(InstrumentSerializer):
        required_fields = ('name',)

    composition = SerializableRelatedField(
        queryset=Composition.objects.all(),
        serializer=CompositionSerializer
    )
    instrument = SerializableRelatedField(
        queryset=Instrument.objects.all(),
        serializer=NestedInstrumentSerializer
    )
    track = serializers.ListField(child=serializers.ListField(child=serializers.CharField()))

    class Meta:
        model = Track
        fields = ('id', 'composition', 'track', 'instrument')


# noinspection PyAbstractClass
class TrackHistorySerializer(serializers.ModelSerializer):
    track = serializers.ListField(child=serializers.ListField(child=serializers.CharField()))
    modified_by = SerializableRelatedField(queryset=User.objects.all(), serializer=UserSerializer)

    class Meta:
        model = TrackHistory
        fields = ('id', 'track', 'track_key', 'modified_by')
