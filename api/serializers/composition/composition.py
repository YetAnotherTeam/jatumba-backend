from django.contrib.auth import get_user_model
from guardian.shortcuts import get_perms
from rest_framework import serializers

from api.models import Band, Composition, Fork, LastCompositionVersionLink
from utils.django_rest_framework.serializers import DynamicFieldsMixin

from .composition_version import CompositionVersionSerializer

User = get_user_model()


class _CompositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Composition
        fields = ('name', 'id', 'band')


class _AsDestinationForkSerializer(serializers.ModelSerializer):
    source_composition = _CompositionSerializer()

    class Meta:
        model = Fork
        fields = ('source_composition',)


class _AsSourceForksSerializer(serializers.ModelSerializer):
    destination_composition = _CompositionSerializer()

    class Meta:
        model = Fork
        fields = ('destination_composition',)


class CompositionSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    latest_version = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    as_destination_fork = _AsDestinationForkSerializer(read_only=True)
    as_source_forks = _AsSourceForksSerializer(read_only=True, many=True)

    class Meta:
        model = Composition
        fields = '__all__'

    def get_latest_version(self, composition):
        try:
            last_composition_version_link = composition.last_composition_version_link
            return CompositionVersionSerializer(
                last_composition_version_link.composition_version
            ).data
        except LastCompositionVersionLink.DoesNotExist:
            return None

    def get_permissions(self, composition):
        return get_perms(self.context['request'].user, composition)


class _BandSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    user_joined = serializers.SerializerMethodField()

    class Meta:
        model = Band
        fields = ('id', 'name', 'description', 'user_joined')

    def get_user_joined(self, band):
        return band.members.filter(user=self.context['request'].user).exists()


class CompositionRetrieveSerializer(CompositionSerializer):
    band = _BandSerializer()


class CompositionListItemSerializer(CompositionSerializer):
    required_fields = ('id', 'name', 'band', 'fork', 'as_destination_fork')
