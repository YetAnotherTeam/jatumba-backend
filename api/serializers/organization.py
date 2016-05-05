from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from api.models import *
from api.serializers import CompositionSerializer
from api.serializers.auth import UserSerializer
from utils.django_rest_framework.fields import SerializableRelatedField
from utils.django_rest_framework.serializers import DynamicFieldsMixin


# noinspection PyAbstractClass
class BandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Band
        fields = ('id', 'name', 'description')


# noinspection PyAbstractClass
class MemberSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    user = SerializableRelatedField(serializer=UserSerializer)
    band = SerializableRelatedField(serializer=BandSerializer)

    class Meta:
        model = Member
        fields = ('id', 'user', 'band')
        validators = [
            UniqueTogetherValidator(
                queryset=Member.objects.all(),
                fields=('user', 'band'),
                message='Вы уже состоите в этой группе',
            )
        ]


class UserRetrieveSerializer(UserSerializer):
    members = MemberSerializer(required_fields=('id', 'band'), many=True)
    instruments = serializers.PrimaryKeyRelatedField(queryset=Instrument.objects.all(), many=True)
    compositions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'phone', 'vk_profile', 'fb_profile',
                  'members', 'instruments', 'compositions')
        extra_kwargs = {'vk_profile': {'read_only': True}, 'fb_profile': {'read_only': True}}

    def get_compositions(self, user):
        # TODO добавить порядок
        return CompositionSerializer(
            Composition.objects.filter(band__members__user=user.id).order_by(),
            required_fields=('id', 'latest_version', 'name', 'band', 'genres'),
            many=True
        ).data
