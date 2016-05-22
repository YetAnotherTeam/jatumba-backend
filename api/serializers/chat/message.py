from rest_framework import serializers

from api.models import Message

from ..auth import UserSerializer


class NestedUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = ('id', 'first_name', 'last_name', 'avatar')


class MessageSerializer(serializers.ModelSerializer):
    author = NestedUserSerializer(read_only=True)

    class Meta:
        model = Message
        exclude = ('band',)


# noinspection PyAbstractClass
class MessagesSerializer(serializers.Serializer):
    messages = MessageSerializer(many=True)
