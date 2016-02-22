from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from oauth2_provider.views import ProtectedResourceView
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from django.db import IntegrityError

from api.auth.auth_providers.vk_api import Vk
from api.serializers import SessionSerializer
from api.models import Session
from api.auth.session_generator import generate_identity


class HelloView(ProtectedResourceView):
    """
    A GET endpoint that needs OAuth2 authentication
    """

    def get(self, request, *args, **kwargs):
        return HttpResponse('Hello, World!')


class SignUpView(APIView):
    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        try:
            user = User.objects.create_user(username, password=password, first_name=first_name, last_name=last_name)
            user.save()
        except IntegrityError:
            return JsonResponse({'error': 'already registered'}, status=400)
        identity = generate_identity()
        session = Session.objects.create(access_token=identity['access_token'], refresh_token=identity['refresh_token'],
                                         time=identity['last_update'], user=user)
        session.save()
        return HttpResponse(JSONRenderer().render(SessionSerializer(session).data), content_type="application/json")


class VkAuth(APIView):
    def get(self, request):
        token = request.GET['token']
        vk_api = Vk()
        user_data = vk_api.get_user_data(token)
        return HttpResponse(user_data['user_id'])
