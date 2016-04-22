from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

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
    user = SerializableRelatedField(serializer=UserSerializer)
    band = SerializableRelatedField(serializer=BandSerializer)
    instrument = SerializableRelatedField(
        allow_null=True,
        required=False,
        serializer=InstrumentSerializer,
        serializer_params={'required_fields': ('name',)}
    )

    class Meta:
        model = Member
        fields = ('id', 'user', 'band', 'instrument')
        validators = [
            UniqueTogetherValidator(
                queryset=Member.objects.all(),
                fields=('user', 'band'),
                message='Вы уже состоите в этой группе',
            )
        ]
