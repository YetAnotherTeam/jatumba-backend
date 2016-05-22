from django.db.transaction import atomic
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.models import Band, CompositionVersion, Fork

from .composition import CompositionSerializer


class ForkSerializer(serializers.ModelSerializer):
    band = serializers.PrimaryKeyRelatedField(queryset=Band.objects.all())
    composition = CompositionSerializer(read_only=True)

    class Meta:
        model = Fork
        fields = ('id', 'band', 'composition', 'composition_version')
        extra_kwargs = {'band': {'write_only': True}}

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
