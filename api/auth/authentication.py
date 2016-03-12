import time

from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication

from api.models import Session


class TokenAuthentication(BaseAuthentication):
    SESSION_EXPIRE_TIME = 3600000

    def authenticate(self, request):
        token = request.META.get('HTTP_TOKEN')
        if not token:
            return None

        session = Session.objects.filter(access_token=token).first()
        if session is None:
            raise exceptions.AuthenticationFailed('No such token')

        if time.time() - session.time > self.SESSION_EXPIRE_TIME:
            raise exceptions.AuthenticationFailed('Token expired')
        return session.user, session.access_token
