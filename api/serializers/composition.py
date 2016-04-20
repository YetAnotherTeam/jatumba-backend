# noinspection PyAbstractClass
from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.models import Composition, Track, CompositionVersion, Instrument

User = get_user_model()


# noinspection PyAbstractClass
class TrackSerializer(serializers.ModelSerializer):
    instrument = serializers.PrimaryKeyRelatedField(queryset=Instrument.objects.all())
    entity = serializers.ListField(child=serializers.ListField(child=serializers.CharField()))

    class Meta:
        model = Track
        fields = ('id', 'entity', 'instrument')


class CompositionVersionSerializer(serializers.ModelSerializer):
    tracks = TrackSerializer(many=True)

    class Meta:
        model = CompositionVersion
        fields = '__all__'

    def create(self, validated_data):
        tracks = validated_data.pop('tracks')
        composition_version = CompositionVersion.objects.create(**validated_data)
        for track in tracks:
            track['composition_version'] = composition_version
        self.fields['tracks'].create(tracks)
        return composition_version


class CompositionSerializer(serializers.ModelSerializer):
    versions = CompositionVersionSerializer(many=True, read_only=True)
    latest_version = serializers.SerializerMethodField()

    class Meta:
        model = Composition
        fields = '__all__'

    def get_latest_version(self, composition):
        return CompositionVersionSerializer(composition.versions.last()).data
