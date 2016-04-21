# noinspection PyAbstractClass
from django.contrib.auth import get_user_model
from django.db.transaction import atomic
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.models import Composition, Track, CompositionVersion, Instrument
from utils.django_rest_framework.serializers import ObjectListSerializer

User = get_user_model()


class TrackListSerializer(ObjectListSerializer):
    pass


# noinspection PyAbstractClass
class TrackSerializer(serializers.ModelSerializer):
    instrument = serializers.PrimaryKeyRelatedField(queryset=Instrument.objects.all())
    entity = serializers.ListField(child=serializers.ListField(child=serializers.IntegerField()))

    class Meta:
        model = Track
        fields = ('id', 'entity', 'instrument')
        list_serializer_class = TrackListSerializer

    def validate_entity(self, entity):
        if len(entity) == 0:
            raise ValidationError('В дорожке должен быть хотя бы один сектор')
        # for sector in entity:
        #     if len(sector) != Track.SECTOR_LENGTH:
        #         raise ValidationError('Сектор должен состоять из %d звуков.' % Track.SECTOR_LENGTH)
        return entity

    def validate(self, track):
        entity = track.get('entity') or self.instance.entity
        instrument = track.get('instrument') or self.instance.instrument
        sounds_ids = instrument.sounds.values_list('id', flat=True)
        for sector in entity:
            for sound_id in sector:
                if sound_id not in sounds_ids:
                    raise ValidationError(
                        'У этого инструмента c id {instrument_id} нет звука с id {sound_id}'
                            .format(
                                instrument_id=instrument.id,
                                sound_id=sound_id
                            )
                    )
        return track


class CompositionVersionSerializer(serializers.ModelSerializer):
    tracks = TrackSerializer(many=True)

    class Meta:
        model = CompositionVersion
        fields = '__all__'

    @atomic
    def create(self, validated_data):
        tracks = validated_data.pop('tracks')
        composition_version = CompositionVersion.objects.create(**validated_data)
        for track in tracks:
            track['composition_version'] = composition_version
        self.fields['tracks'].create(tracks)
        return composition_version

    @atomic
    def update(self, instance, validated_data):
        tracks = validated_data.get('tracks')
        for track in tracks:
            track['composition_version'] = instance
        self.fields['tracks'].update(instance.tracks.all(), tracks)
        return instance


class CompositionSerializer(serializers.ModelSerializer):
    versions = CompositionVersionSerializer(many=True, read_only=True)
    latest_version = serializers.SerializerMethodField()

    class Meta:
        model = Composition
        fields = '__all__'

    def get_latest_version(self, composition):
        return CompositionVersionSerializer(composition.versions.last()).data
