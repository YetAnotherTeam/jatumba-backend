from django.contrib.auth import get_user_model
from guardian.shortcuts import get_perms
from rest_framework import serializers

from api.models import Band, Composition, Fork
from utils.django_rest_framework.serializers import DynamicFieldsMixin

from .composition_version import CompositionVersionSerializer

User = get_user_model()


class NestedCompositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Composition
        fields = ('name', 'id', 'band')


class NestedAsDestinationForkSerializer(serializers.ModelSerializer):
    source_composition = NestedCompositionSerializer()

    class Meta:
        model = Fork
        fields = ('source_composition',)


class NestedAsSourceForksSerializer(serializers.ModelSerializer):
    destination_composition = NestedCompositionSerializer()

    class Meta:
        model = Fork
        fields = ('destination_composition',)


class CompositionSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    latest_version = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    as_destination_fork = NestedAsDestinationForkSerializer(read_only=True)
    as_source_forks = NestedAsSourceForksSerializer(read_only=True, many=True)

    class Meta:
        model = Composition
        fields = '__all__'

    def get_latest_version(self, composition):
        return CompositionVersionSerializer(composition.versions.last()).data

    def get_permissions(self, composition):
        return get_perms(self.context['request'].user, composition)


class NestedBandSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    user_joined = serializers.SerializerMethodField()

    class Meta:
        model = Band
        fields = ('id', 'name', 'description', 'user_joined')

    def get_user_joined(self, band):
        return band.members.filter(user=self.context['request'].user).exists()


class CompositionRetrieveSerializer(CompositionSerializer):
    band = NestedBandSerializer()


class CompositionListItemSerializer(CompositionSerializer):
    required_fields = ('id', 'name', 'band', 'fork', 'as_destination_fork')
