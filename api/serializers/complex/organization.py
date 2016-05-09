from rest_framework import serializers

from api.models import *
from api.serializers.complex.composition import CompositionSerializer
from api.serializers.elementary.organization import BandSerializer
from api.serializers.elementary.auth import UserSerializer
from utils.django_rest_framework.fields import SerializableRelatedField
from utils.django_rest_framework.serializers import DynamicFieldsMixin


class MemberSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    band = SerializableRelatedField(
        serializer=BandSerializer,
        serializer_params={'required_fields': ('id', 'name', 'description')}
    )

    class Meta:
        model = Member
        fields = ('id', 'user', 'band')
