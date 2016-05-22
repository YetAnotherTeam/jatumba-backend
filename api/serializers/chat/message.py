from rest_framework import serializers

from api.models import Message, User


class NestedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'avatar')


class MessageSerializer(serializers.ModelSerializer):
    author = NestedUserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ('id', 'author', 'datetime', 'text')


# noinspection PyAbstractClass
class MessagesSerializer(serializers.Serializer):
    messages = MessageSerializer(many=True)
