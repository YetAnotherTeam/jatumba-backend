import time
from rest_framework.authentication import BaseAuthentication
from api.models import Session
from rest_framework import exceptions


class TokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.META.token
        print('!!!!' + '1')
        if not token:
            return None
        print('!!!!' + '2')
        try:
            session = Session.objects.filter(access_token=token)
        except Session.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such token')
        print('!!!!' + '3')
        if session['time'] - time.time() > 3600:
            return None
        print('!!!!' + '4')
        return session['user'], session['access_token']
