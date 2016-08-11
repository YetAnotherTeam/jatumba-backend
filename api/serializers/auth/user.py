from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.models import Band, Composition, LastCompositionVersionLink, Member, Fork
from utils.django_rest_framework.fields import SerializableRelatedField
from utils.django_rest_framework.serializers import DynamicFieldsMixin
from ..composition.composition_version import CompositionVersionSerializer

User = get_user_model()


class _MemberBandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Band
        fields = ('id', 'name', 'description', 'create_datetime')


class _MemberSerializer(serializers.ModelSerializer):
    band = SerializableRelatedField(serializer=_MemberBandSerializer)

    class Meta:
        model = Member
        fields = ('id', 'band')


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


class _BandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Band
        fields = ('id', 'name')


class _ForkCompositionSerializer(serializers.ModelSerializer):
    band = _BandSerializer()

    class Meta:
        model = Composition
        fields = ('band',)


class _AsDestinationForkSerializer(serializers.ModelSerializer):
    source_composition = _ForkCompositionSerializer()

    class Meta:
        model = Fork
        fields = ('source_composition',)


class _CompositionSerializer(serializers.ModelSerializer):
    latest_version = serializers.SerializerMethodField()
    as_destination_fork = _AsDestinationForkSerializer(read_only=True)

    class Meta:
        model = Composition
        fields = ('id', 'latest_version', 'as_destination_fork', 'name', 'band', 'genres')

    def get_latest_version(self, composition):
        try:
            last_composition_version_link = composition.last_composition_version_link
            return CompositionVersionSerializer(
                last_composition_version_link.composition_version,
                context=self.context
            ).data
        except LastCompositionVersionLink.DoesNotExist:
            return None


class UserRetrieveSerializer(UserSerializer):
    members = _MemberSerializer(many=True)
    compositions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'phone', 'vk_profile', 'fb_profile',
                  'members', 'instruments', 'compositions', 'avatar')
        extra_kwargs = {'vk_profile': {'read_only': True}, 'fb_profile': {'read_only': True}}

    def get_compositions(self, user):
        return _CompositionSerializer(
            Composition.objects
            .filter(band__members__user=user.id)
            .select_related('last_composition_version_link__composition_version')
            .order_by('-last_composition_version_link__composition_version__create_datetime')
            .prefetch_related(
                'genres',
                'last_composition_version_link__composition_version__tracks'
            ),
            many=True,
            context=self.context
        ).data
