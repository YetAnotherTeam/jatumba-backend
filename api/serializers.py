from rest_framework import serializers

from api.models import *
from utils.django_rest_framework_utils import DeserializePrimaryKeyRelatedField


# noinspection PyAbstractClass
class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'password', 'first_name', 'last_name')


# noinspection PyAbstractClass
class SignInSerializer(serializers.Serializer):
    username = serializers.CharField(label='Юзернейм')
    password = serializers.CharField(style={'input_type': 'password'}, label='Пароль')


# noinspection PyAbstractClass
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'phone', 'vk_profile', 'fb_profile')
        extra_kwargs = {'vk_profile': {'read_only': True}, 'fb_profile': {'read_only': True}}


# noinspection PyAbstractClass
class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ('access_token', 'refresh_token')


# noinspection PyAbstractClass
class AuthResponseSerializer(serializers.Serializer):
    user = UserSerializer()
    session = SessionSerializer()


# noinspection PyAbstractClass
class BandSerializer(serializers.ModelSerializer):
    name = serializers.CharField(allow_blank=False, max_length=50)

    class Meta:
        model = Band


# noinspection PyAbstractClass
class CompositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Composition


class SoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sound
        fields = ('id', 'name', 'file')


# noinspection PyAbstractClass
class InstrumentSerializer(serializers.ModelSerializer):
    sounds = SoundSerializer(many=True)

    class Meta:
        model = Instrument
        fields = ('id', 'name', 'sounds')

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super(InstrumentSerializer, self).__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)


# noinspection PyAbstractClass
class BandMemberSerializer(serializers.ModelSerializer):
    user = DeserializePrimaryKeyRelatedField(queryset=User.objects.all(), serializer=UserSerializer)
    band = DeserializePrimaryKeyRelatedField(queryset=Band.objects.all(), serializer=BandSerializer)
    instrument = DeserializePrimaryKeyRelatedField(queryset=Instrument.objects.all(),
                                                   serializer=InstrumentSerializer)

    class Meta:
        model = Member
        fields = ('id', 'user', 'band', 'instrument')
