from django.db.transaction import atomic
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.models import Band, CompositionVersion, Fork

from .composition import CompositionSerializer


class ForkSerializer(serializers.ModelSerializer):
    source_composition = CompositionSerializer(read_only=True)
    destination_composition = CompositionSerializer(read_only=True)

    class Meta:
        model = Fork
        fields = ('id', 'source_composition', 'destination_composition',
                  'source_composition_version')


class ForkCreateSerializer(serializers.ModelSerializer):
    band = serializers.PrimaryKeyRelatedField(queryset=Band.objects.all(), write_only=True)
    destination_composition = CompositionSerializer(read_only=True)

    class Meta:
        model = Fork
        fields = ('id', 'band', 'source_composition', 'source_composition_version',
                  'destination_composition')
        extra_kwargs = {
            'source_composition': {'read_only': True},
            'destination_composition': {'read_only': True}
        }

    def validate(self, attrs):
        request = self.context['request']
        user = request.user
        band = attrs['band']
        if not band.members.filter(user=user).exists():
            raise ValidationError('Вы не состоите в этой группе')
        return attrs

    @atomic
    def create(self, validated_data):
        source_composition_version = validated_data['source_composition_version']
        source_composition = source_composition_version.composition
        source_composition_id = source_composition.id

        # Создаем новую композицию.
        destination_composition = source_composition
        destination_composition.id = None
        destination_composition.band_id = validated_data['band'].id
        destination_composition.save()
        # Создаем новую версию новой композиции
        destination_composition_version = CompositionVersion.objects.create(
            composition=destination_composition,
            author=source_composition_version.author
        )

        # Копируем дорожки
        for track in source_composition_version.tracks.all():
            track.id = None
            track.composition_version_id = destination_composition_version.id
            track.save()

        # Создаем форк
        fork = Fork.objects.create(
            source_composition_id=source_composition_id,
            source_composition_version=source_composition_version,
            destination_composition=destination_composition,
        )
        return fork
