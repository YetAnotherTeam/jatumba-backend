# noinspection PyAbstractClass
from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.models import (
    Composition, Track, CompositionVersion
)
from api.serializers.dictionary import InstrumentSerializer
from utils.django_rest_framework.fields import SerializableRelatedField

User = get_user_model()


class CompositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Composition


class CompositionVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompositionVersion


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
