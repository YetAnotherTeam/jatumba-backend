from rest_framework import serializers

from api.models import Message, User


class _UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'avatar', 'username')


class MessageSerializer(serializers.ModelSerializer):
    author = _UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ('id', 'author', 'datetime', 'text')


# noinspection PyAbstractClass
class MessagesSerializer(serializers.Serializer):
    messages = MessageSerializer(many=True)
