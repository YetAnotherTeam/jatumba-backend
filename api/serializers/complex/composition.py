# noinspection PyAbstractClass
from django.contrib.auth import get_user_model
from django.db.transaction import atomic
from guardian.shortcuts import get_perms
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.models import Composition, Track, CompositionVersion, Instrument, Fork, Band
from api.serializers.elementary.organization import BandSerializer
from utils.django_rest_framework.fields import NoneableIntegerField
from utils.django_rest_framework.serializers import ObjectListSerializer, DynamicFieldsMixin

User = get_user_model()


class TrackListSerializer(ObjectListSerializer):
    pass


class TrackSerializer(serializers.ModelSerializer):
    instrument = serializers.PrimaryKeyRelatedField(queryset=Instrument.objects.all())
    entity = serializers.ListField(
        child=serializers.ListField(child=NoneableIntegerField(allow_null=True))
    )

    class Meta:
        model = Track
        fields = ('id', 'entity', 'instrument', 'order')
        extra_kwargs = {'order': {'write_only': True}}
        list_serializer_class = TrackListSerializer

    def validate_entity(self, entity):
        if len(entity) == 0:
            raise ValidationError('В дорожке должен быть хотя бы один сектор')
        for sector in entity:
            if len(sector) != Track.SECTOR_LENGTH:
                raise ValidationError('Сектор должен состоять из %d звуков.' % Track.SECTOR_LENGTH)
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
                            .format(
                            instrument_id=instrument.id,
                            sound_id=sound_id
                        )
                    )
        return track


class CompositionVersionSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    tracks = TrackSerializer(many=True)

    class Meta:
        model = CompositionVersion
        fields = '__all__'
        extra_kwargs = {'composition': {'write_only': True}}

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


class DiffTrackSerializer(serializers.ModelSerializer):
    instrument = serializers.PrimaryKeyRelatedField(queryset=Instrument.objects.all())
    entity = serializers.ListField(
        child=serializers.ListField(child=NoneableIntegerField(allow_null=True))
    )

    class Meta:
        model = Track
        fields = ('id', 'entity', 'instrument', 'order')
        list_serializer_class = TrackListSerializer

    def validate_entity(self, entity):
        if len(entity) == 0:
            raise ValidationError('В дорожке должен быть хотя бы один сектор')
        for sector in entity:
            if len(sector) != Track.SECTOR_LENGTH:
                raise ValidationError('Сектор должен состоять из %d звуков.' % Track.SECTOR_LENGTH)
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
                            .format(
                            instrument_id=instrument.id,
                            sound_id=sound_id
                        )
                    )
        return track


# class DiffCompositionVersionSerializer(serializers.ModelSerializer):
#     diff_tracks = DiffTrackSerializer()


class CompositionSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    latest_version = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = Composition
        fields = '__all__'

    def get_latest_version(self, composition):
        return CompositionVersionSerializer(composition.versions.last()).data

    def get_permissions(self, composition):
        return get_perms(self.context['request'].user, composition)


class CompositionRetrieveSerializer(CompositionSerializer):
    band = BandSerializer()


class CompositionListItemSerializer(CompositionSerializer):
    required_fields = ('id', 'name', 'band')


# noinspection PyAbstractClass
class ForkCreateSerializer(serializers.Serializer):
    band = serializers.PrimaryKeyRelatedField(queryset=Band.objects.all())

    def validate(self, attrs):
        request = self.context['request']
        user = request.user
        band = attrs['band']
        if not band.members.filter(user=user).exists():
            raise ValidationError('Вы не состоите в этой группе')
        return attrs


# noinspection PyAbstractClass
class ForkSerializer(serializers.ModelSerializer):
    composition_version = serializers.PrimaryKeyRelatedField(
        queryset=CompositionVersion.objects.all()
    )
    composition = CompositionSerializer()

    class Meta:
        model = Fork
        fields = '__all__'
