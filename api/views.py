import os

import binascii
from django.http import HttpResponse, JsonResponse
from rest_framework.permissions import IsAuthenticated
from api.auth.authentication import TokenAuthentication
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from django.db import IntegrityError

from api.auth.auth_providers.vk_api import Vk
from api.serializers import *
from api.models import Session
from api.auth.session_generator import generate_identity


class SignUpView(APIView):
    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        try:
            user = User.objects.create_user('rg' + username, password=password, first_name=first_name, last_name=last_name)
            user.profile.public_username = username
            user.save()
        except IntegrityError:
            return JsonResponse({'error': 'already registered'}, status=400)
        identity = generate_identity()
        session = Session.objects.create(access_token=identity['access_token'], refresh_token=identity['refresh_token'],
                                         time=identity['last_update'], user=user)
        session.save()
        return HttpResponse(JSONRenderer().render(SessionSerializer(session).data), content_type="application/json")


class VkAuth(APIView):
    def post(self, request):
        token = request.POST['token']
        vk_api = Vk()
        user_data = vk_api.get_user_data(token)
        username = 'vk' + user_data['user_id']
        user = User.objects.filter(username=username)
        if user is None:
            try:
                user = User.objects.create_user(username, password=binascii.hexlify(os.urandom(10)).decode('utf-8'),
                                                first_name=user_data['first_name'], last_name=user_data['last_name'])
                user.save()
            except IntegrityError:
                return JsonResponse({'error': 'already registered'}, status=400)
        identity = generate_identity()
        session = Session.objects.create(access_token=identity['access_token'], refresh_token=identity['refresh_token'],
                                         time=identity['last_update'], user=user)
        session.save()
        return HttpResponse(JSONRenderer().render(SessionSerializer(session).data), content_type="application/json")


class RefreshToken(APIView):
    def post(self, request):
        refresh_token = request.POST['refresh_token']
        session = Session.objects.filter(refresh_token=refresh_token)
        if session is None:
            return JsonResponse({'error': 'invalid token'}, status=400)
        identity = generate_identity()
        new_session = Session.objects.create(access_token=identity['access_token'],
                                             refresh_token=identity['refresh_token'],
                                             time=identity['last_update'], user=session.user)
        new_session.save()
        session.delete()
        return HttpResponse(JSONRenderer().render(SessionSerializer(new_session).data), content_type="application/json")


class ProfileView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, username):
        user = User.objects.filter(username=username).first()
        if user is None:
            return JsonResponse({'error': 'no such user'}, status=404)
        return HttpResponse(JSONRenderer().render(UserSerializer(user).data), content_type="application/json")
