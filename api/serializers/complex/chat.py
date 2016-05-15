from rest_framework import serializers

from api.models.chat import Message
from api.serializers.elementary.chat import MessageSerializer
from api.serializers.elementary.auth import UserSerializer


class MessageCreateSerializer(MessageSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Message
        exclude = ('band',)


# noinspection PyAbstractClass
class MessagesSerializer(serializers.Serializer):
    messages = MessageCreateSerializer(many=True)
