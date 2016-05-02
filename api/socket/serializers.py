from django.contrib.auth import get_user_model
from rest_framework import serializers, fields

from api.serializers import CompositionVersionSerializer

User = get_user_model()


# noinspection PyAbstractClass,PyProtectedMember
class ResponseSocketSerializer(serializers.Serializer):
    status = serializers.IntegerField(min_value=100, max_value=600)
    method = serializers.CharField()
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())


# noinspection PyAbstractClass
class SignInSocketSerializer(serializers.Serializer):
    access_token = serializers.CharField()


# noinspection PyAbstractClass
class CompositionVersionResponseSocketSerializer(ResponseSocketSerializer):
    data = CompositionVersionSerializer()
