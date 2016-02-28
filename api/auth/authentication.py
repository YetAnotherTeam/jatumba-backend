import time

from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication

from api.models import Session


class TokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.META.get('HTTP_TOKEN')
        print(token)
        if not token:
            return None
        try:
            session = Session.objects.filter(access_token=token).first()
        except Session.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such token')
        if session.time - time.time() > 3600:
            return None
        return session.user, session.access_token
