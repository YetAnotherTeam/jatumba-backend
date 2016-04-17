# noinspection PyAbstractClass
from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.models import (
    Composition, Track, CompositionBranch, TrackSnapshot, TrackDiff
)
from api.serializers.dictionary import InstrumentSerializer
from utils.django_rest_framework.fields import SerializableRelatedField

User = get_user_model()


class CompositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Composition


class CompositionBranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompositionBranch


# noinspection PyAbstractClass
class TrackSerializer(serializers.ModelSerializer):
    composition = SerializableRelatedField(serializer=CompositionSerializer)
    instrument = SerializableRelatedField(
        serializer=InstrumentSerializer,
        serializer_params={'required_fields': ('name',)},
    )

    class Meta:
        model = Track
        fields = ('id', 'composition', 'instrument')


class TrackSnapshotSerializer(serializers.ModelSerializer):
    entity = serializers.ListField(child=serializers.ListField(child=serializers.CharField()))

    class Meta:
        model = TrackSnapshot
        fields = '__all__'


class TrackDiffSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackDiff
        fields = '__all__'
