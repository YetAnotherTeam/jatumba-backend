from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


# noinspection PyAbstractClass
class SignInSocketSerializer(serializers.Serializer):
    access_token = serializers.CharField()
