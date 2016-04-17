from rest_framework import serializers

from api.models import *
from api.serializers.auth import UserSerializer
from api.serializers.dictionary import InstrumentSerializer
from utils.django_rest_framework.fields import SerializableRelatedField


# noinspection PyAbstractClass
class BandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Band
        fields = ('id', 'name', 'description')


# noinspection PyAbstractClass
class MemberSerializer(serializers.ModelSerializer):
    user = SerializableRelatedField(queryset=User.objects.all(), serializer=UserSerializer)
    band = SerializableRelatedField(queryset=Band.objects.all(), serializer=BandSerializer)
    instrument = SerializableRelatedField(
        queryset=Instrument.objects.all(),
        allow_null=True,
        required=False,
        serializer=InstrumentSerializer,
        serializer_params={'fields': ('name',)}
    )

    class Meta:
        model = Member
        validators = []
        fields = ('id', 'user', 'band', 'instrument', 'leader')
        extra_kwargs = {'leader': {'read_only': True}}
