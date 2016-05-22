from rest_framework import serializers

from api.models import Message

from ..auth import UserSerializer


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        exclude = ('band',)


class MessageCreateSerializer(MessageSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Message
        exclude = ('band',)


# noinspection PyAbstractClass
class MessagesSerializer(serializers.Serializer):
    messages = MessageCreateSerializer(many=True)
