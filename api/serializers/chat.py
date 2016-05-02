from rest_framework import serializers

from api.models.chat import Message
from api.serializers import UserSerializer


class MessageSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Message
        exclude = ('band',)


# noinspection PyAbstractClass
class MessagesSerializer(serializers.Serializer):
    messages = MessageSerializer(many=True)
