from django.contrib.auth import get_user_model
from django.db.transaction import atomic
from rest_framework import serializers

from api.models import CompositionVersion, DiffCompositionVersion
from utils.django_rest_framework.serializers import DynamicFieldsMixin
from .track import DiffTrackSerializer, TrackSerializer

User = get_user_model()


class _UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'avatar', 'username')


class CompositionVersionSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    tracks = TrackSerializer(many=True)
    author = _UserSerializer(read_only=True)

    class Meta:
        model = CompositionVersion
        fields = ('id', 'author', 'tracks', 'create_datetime')
        extra_kwargs = {
            'composition': {'write_only': True}
        }

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
