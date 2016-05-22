from rest_framework import serializers

from api.models import Member
from utils.django_rest_framework.fields import SerializableRelatedField
from utils.django_rest_framework.serializers import DynamicFieldsMixin

from ..auth.user import UserSerializer
from .band import BandSerializer


class MemberSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    user = SerializableRelatedField(serializer=UserSerializer)
    band = SerializableRelatedField(
        serializer=BandSerializer,
        serializer_params={'required_fields': ('id', 'name', 'description')}
    )

    class Meta:
        model = Member
        fields = ('id', 'user', 'band')
