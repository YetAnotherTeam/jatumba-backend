from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.models import Band, Composition, Instrument, Member
from utils.django_rest_framework.fields import SerializableRelatedField
from utils.django_rest_framework.serializers import DynamicFieldsMixin

from ..composition import CompositionSerializer

User = get_user_model()


class NestedBandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Band
        fields = ('id', 'name', 'description')


class NestedMemberSerializer(serializers.ModelSerializer):
    required_fields = ('id', 'band')
    band = SerializableRelatedField(serializer=NestedBandSerializer)

    class Meta:
        model = Member


class UserSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'password', 'phone', 'vk_profile',
                  'fb_profile', 'avatar')
        extra_kwargs = {
            'vk_profile': {'read_only': True},
            'fb_profile': {'read_only': True},
            'password': {'write_only': True}
        }


class UserRetrieveSerializer(UserSerializer):
    members = NestedMemberSerializer(many=True)
    instruments = serializers.PrimaryKeyRelatedField(queryset=Instrument.objects.all(), many=True)
    compositions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'phone', 'vk_profile', 'fb_profile',
                  'members', 'instruments', 'compositions')
        extra_kwargs = {'vk_profile': {'read_only': True}, 'fb_profile': {'read_only': True}}

    def get_compositions(self, user):
        # sorted_composition_versions = (
        #     CompositionVersion.objects
        #         .values_list('composition', 'id')
        #         .annotate(Max('create_datetime'))
        #         .filter(composition__band__members__user=user.id)
        #         .order_by('create_datetime__max')
        # )
        return CompositionSerializer(
            Composition.objects.filter(band__members__user=user.id),
            required_fields=('id', 'latest_version', 'name', 'band', 'genres'),
            many=True
        ).data
