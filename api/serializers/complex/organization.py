from rest_framework import serializers

from api.models import Member
from api.serializers.elementary.auth import UserSerializer
from api.serializers.elementary.organization import BandSerializer
from utils.django_rest_framework.fields import SerializableRelatedField
from utils.django_rest_framework.serializers import DynamicFieldsMixin


class MemberSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    user = SerializableRelatedField(serializer=UserSerializer)
    band = SerializableRelatedField(
        serializer=BandSerializer,
        serializer_params={'required_fields': ('id', 'name', 'description')}
    )

    class Meta:
        model = Member
        fields = ('id', 'user', 'band')
