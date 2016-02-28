import os

import binascii

from django.contrib.auth import authenticate
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from api.auth.auth_providers.fb_api import Fb
from api.auth.auth_providers.vk_api import Vk

from api.auth.authentication import TokenAuthentication
from api.auth.session_generator import generate_identity
from api.models import Session
from api.serializers import *


class SignUpView(APIView):
    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        try:
            user = User.objects.create_user(username, password=password, first_name=first_name,
                                            last_name=last_name)
            user.save()
        except IntegrityError:
            return JsonResponse({'error': 'username already taken'}, status=400)
        session = generate_session(user)
        return Response(SessionSerializer(session).data, content_type="application/json")


class SignInView(APIView):
    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            return Response(SessionSerializer(generate_session(user)).data, content_type="application/json")
        else:
            return Response({'error': 'wrong username or password'}, status=401, content_type="application/json")


class VkAuth(APIView):
    def post(self, request):
        token = request.POST['token']
        vk_api = Vk()
        user_data = vk_api.get_user_data(token)
        profile = models.Profile.objects.filter(vk_profile=user_data['user_id']).first()
        if profile:
            return Response(SessionSerializer(generate_session(profile.user)).data, content_type="application/json")
        else:
            return social_auth(user_data, request)


class FbAuth(APIView):
    def post(self, request):
        token = request.POST['token']
        fb_api = Fb()
        user_data = fb_api.get_user_data(token)
        profile = models.Profile.objects.filter(fb_profile=user_data['user_id']).first()
        if profile:
            return Response(SessionSerializer(generate_session(profile.user)).data, content_type="application/json")
        else:
            return social_auth(user_data, request)


def social_auth(user_data, request):
    try:
        username = request.POST['username']
    except MultiValueDictKeyError:
        return Response({'error': 'user not found, register new by including username in request'}, status=404)
    user = User.objects.filter(username=username).first()
    if user:
        return JsonResponse({'error': 'username already taken'}, status=400)
    user = User.objects.create_user(username, password=binascii.hexlify(os.urandom(10)).decode('utf-8'),
                                    first_name=user_data['first_name'], last_name=user_data['last_name'])

    profile = user.profile
    if user_data['network'] is 'fb':
        profile.fb_profile = user_data['user_id']
    elif user_data['network'] is 'vk':
        profile.vk_profile = user_data['user_id']
    profile.save()
    user.save()
    session = generate_session(user)
    return Response(SessionSerializer(session).data, content_type="application/json")


def generate_session(user):
    identity = generate_identity()
    session = Session.objects.create(access_token=identity['access_token'], refresh_token=identity['refresh_token'],
                                     time=identity['last_update'], user=user)
    session.save()
    return session


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
        return Response(SessionSerializer(new_session).data, content_type="application/json")


class ProfileView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, username):
        profile = Profile.objects.filter(public_username=username).first()
        if profile is None:
            user = User.objects.filter(username=username).first()
            if user is None:
                return JsonResponse({'error': 'no such user'}, status=404)
        else:
            user = profile.user
        return Response(UserSerializer(user).data, content_type="application/json")
