from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.models import AbstractTrack, DiffTrack, Track
from utils.django_rest_framework.fields import NoneableIntegerField
from utils.django_rest_framework.serializers import ObjectListSerializer


class TrackListSerializer(ObjectListSerializer):
    pass


class BaseTrackSerializer(serializers.ModelSerializer):
    entity = serializers.ListField(
        child=serializers.ListField(child=NoneableIntegerField(allow_null=True))
    )

    class Meta:
        fields = ('id', 'entity', 'instrument', 'order')
        extra_kwargs = {'order': {'write_only': True}}
        list_serializer_class = TrackListSerializer

    def validate_entity(self, entity):
        if len(entity) == 0:
            raise ValidationError('В дорожке должен быть хотя бы один сектор')
        for sector in entity:
            if len(sector) != AbstractTrack.SECTOR_LENGTH:
                raise ValidationError(
                    'Сектор должен состоять из {sounds_count} звуков.'
                    .format(sounds_count=AbstractTrack.SECTOR_LENGTH)
                )
        return entity

    def validate(self, track):
        entity = track.get('entity') or self.instance.entity
        instrument = track.get('instrument') or self.instance.instrument
        sounds_ids = instrument.sounds.values_list('id', flat=True)
        for sector in entity:
            for sound_id in sector:
                if sound_id is not None and sound_id not in sounds_ids:
                    raise ValidationError(
                        'У инструмента c id {instrument_id} нет звука с id {sound_id}.'
                        .format(instrument_id=instrument.id, sound_id=sound_id)
                    )
        return track


class TrackSerializer(BaseTrackSerializer):
    class Meta(BaseTrackSerializer.Meta):
        model = Track


class DiffTrackSerializer(BaseTrackSerializer):
    class Meta(BaseTrackSerializer.Meta):
        model = DiffTrack
