from rest_framework import serializers

from api.serializers import CompositionVersionSerializer, User


# noinspection PyAbstractClass
class SocketResponseSerializer(serializers.Serializer):
    status = serializers.IntegerField(min_value=100, max_value=600)
    method = serializers.CharField()
    user = serializers.IntegerField()


# noinspection PyAbstractClass
class SocketCompositionVersionSerializer(SocketResponseSerializer):
    data = CompositionVersionSerializer(required_fields=('tracks',))