# noinspection PyAbstractClass
from django.contrib.auth import get_user_model
from django.db.transaction import atomic
from guardian.shortcuts import get_perms
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.models import (
    Band, Composition, CompositionVersion, DiffCompositionVersion, DiffTrack, Fork, Instrument,
    Track
)
from utils.django_rest_framework.fields import NoneableIntegerField
from utils.django_rest_framework.serializers import DynamicFieldsMixin, ObjectListSerializer

from .organization import BandSerializer

User = get_user_model()


class TrackListSerializer(ObjectListSerializer):
    pass


class BaseTrackSerializer(serializers.ModelSerializer):
    instrument = serializers.PrimaryKeyRelatedField(queryset=Instrument.objects.all())
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


class TrackSerializer(BaseTrackSerializer):
    class Meta(BaseTrackSerializer.Meta):
        model = Track


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


class DiffTrackSerializer(BaseTrackSerializer):
    class Meta(BaseTrackSerializer.Meta):
        model = DiffTrack


class DiffCompositionVersionSerializer(serializers.ModelSerializer):
    tracks = DiffTrackSerializer(many=True)

    class Meta:
        model = DiffCompositionVersion
        fields = '__all__'
        extra_kwargs = {'composition': {'write_only': True}}

    @atomic
    def create(self, validated_data):
        diff_tracks = validated_data.pop('tracks')
        diff_composition_version = DiffCompositionVersion.objects.create(**validated_data)
        for diff_track in diff_tracks:
            diff_track['diff_composition_version'] = diff_composition_version
        self.fields['tracks'].create(diff_tracks)
        return diff_composition_version

    @atomic
    def update(self, instance, validated_data):
        diff_tracks = validated_data.get('tracks')
        for diff_track in diff_tracks:
            diff_track['diff_composition_version'] = instance
        self.fields['tracks'].update(instance.tracks.all(), diff_tracks)
        return instance


# noinspection PyAbstractClass
class DiffHistorySerializer(serializers.Serializer):
    diff_composition_version = serializers.PrimaryKeyRelatedField(
        queryset=DiffCompositionVersion.objects.all()
    )

    def validate_diff_composition_version(self, diff_composition_version):
        if self.context['composition_id'] != diff_composition_version.composition_id:
            raise ValidationError('Wrong diff composition version.')
        return diff_composition_version


class CompositionSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class NestedForkSerializer(serializers.ModelSerializer):
        class NestedCompositionVersionSerializer(serializers.ModelSerializer):
            class NestedCompositionSerializer(serializers.ModelSerializer):
                class Meta:
                    model = Composition
                    fields = ('name', 'id', 'band')

            composition = NestedCompositionSerializer()

            class Meta:
                model = CompositionVersion
                fields = ('composition',)

        composition_version = NestedCompositionVersionSerializer()

        class Meta:
            model = Fork
            fields = ('composition_version',)

    latest_version = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    fork = NestedForkSerializer(read_only=True)

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
    required_fields = ('id', 'name', 'band', 'fork')


class ForkCreateSerializer(serializers.ModelSerializer):
    band = serializers.PrimaryKeyRelatedField(queryset=Band.objects.all(), write_only=True)
    composition = CompositionSerializer(read_only=True)

    class Meta:
        model = Fork
        fields = '__all__'

    def validate(self, attrs):
        request = self.context['request']
        user = request.user
        band = attrs['band']
        if not band.members.filter(user=user).exists():
            raise ValidationError('Вы не состоите в этой группе')
        return attrs

    @atomic
    def create(self, validated_data):
        composition_version = validated_data['composition_version']

        # Создаем новую композицию.
        composition = composition_version.composition
        composition.band_id = validated_data['band'].id
        composition.id = None
        composition.save()

        # Создаем новую версию новой композиции
        new_composition_version = CompositionVersion.objects.create(
            composition=composition,
            author=composition_version.author
        )

        # Копируем дорожки
        for track in composition_version.tracks.all():
            track.id = None
            track.composition_version_id = new_composition_version.id
            track.save()

        # Создаем форк
        fork = Fork.objects.create(
            composition=composition,
            composition_version=composition_version
        )
        return fork