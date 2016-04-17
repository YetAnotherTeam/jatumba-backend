from rest_framework import serializers

from api.models import *
from api.serializers.auth import UserSerializer
from utils.django_rest_framework.fields import SerializableRelatedField
from utils.django_rest_framework.serializers import DynamicFieldsMixin


# noinspection PyAbstractClass
class BandSerializer(serializers.ModelSerializer):
    name = serializers.CharField(allow_blank=False, max_length=50)

    class Meta:
        model = Band
        fields = ('id', 'name', 'description', 'leader')


# noinspection PyAbstractClass
class CompositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Composition


class SoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sound
        fields = ('id', 'name', 'file')


# noinspection PyAbstractClass
class InstrumentSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    sounds = SoundSerializer(many=True)

    class Meta:
        model = Instrument
        fields = ('id', 'name', 'sounds')


# noinspection PyAbstractClass
class BandMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    band = SerializableRelatedField(queryset=Band.objects.all(), serializer=BandSerializer)
    instrument = SerializableRelatedField(
        queryset=Instrument.objects.all(),
        serializer=InstrumentSerializer,
        serializer_params={'fields': ('name',)},
        required=False
    )

    class Meta:
        model = Member
        fields = ('id', 'user', 'band', 'instrument')


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
