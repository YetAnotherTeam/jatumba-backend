from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from api.models import Instrument, Composition
from api.models import Session
from api.serializers.composition import CompositionSerializer
from api.serializers.organization import MemberSerializer, BandSerializer
from utils.django_rest_framework.fields import SerializableRelatedField
from .user import UserSerializer

User = get_user_model()


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ('access_token', 'refresh_token')


# noinspection PyAbstractClass
class SignInSerializer(serializers.Serializer):
    username = serializers.CharField(label='Юзернейм')
    password = serializers.CharField(style={'input_type': 'password'}, label='Пароль')


# noinspection PyAbstractClass
class IsAuthenticatedSerializer(serializers.Serializer):
    access_token = serializers.CharField()


class UserRetrieveSerializer(UserSerializer):
    class NestedMemberSerializer(MemberSerializer):
        required_fields = ('id', 'band')
        band = SerializableRelatedField(
            serializer=BandSerializer,
            serializer_params={'required_fields': ('id', 'name', 'description')}
        )

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
            Composition.objects.filter(band__members__user=user.id).order_by(),
            required_fields=('id', 'latest_version', 'name', 'band', 'genres'),
            many=True
        ).data


class SignUpSerializer(UserSerializer):
    required_fields = ('username', 'password', 'first_name', 'last_name', 'avatar')

    class Meta(UserSerializer.Meta):
        extra_kwargs = {
            'vk_profile': {'read_only': True},
            'fb_profile': {'read_only': True}
        }

    def create(self, validated_data):
        if validated_data.get('password'):
            validated_data['password'] = make_password(
                validated_data['password']
            )
        return super(SignUpSerializer, self).create(validated_data)


# noinspection PyAbstractClass
class AuthResponseSerializer(serializers.Serializer):
    user = UserSerializer(read_only=True)
    session = SessionSerializer(read_only=True)
