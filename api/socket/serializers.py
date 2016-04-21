from rest_framework import serializers

from api.serializers import CompositionVersionSerializer


# noinspection PyAbstractClass
class SocketResponseSerializer(serializers.Serializer):
    status = serializers.IntegerField(min_value=100, max_value=600)


# noinspection PyAbstractClass
class SocketCompositionVersionSerializer(SocketResponseSerializer):
    data = CompositionVersionSerializer()
