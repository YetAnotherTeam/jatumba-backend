import binascii

from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.utils.datastructures import MultiValueDictKeyError
from rest_framework import status, viewsets, mixins, filters
from rest_framework.decorators import list_route
from rest_framework.permissions import AllowAny, DjangoObjectPermissions
from rest_framework.response import Response
from rest_framework.views import APIView

from api.auth.auth_providers.fb_api import FB
from api.auth.auth_providers.vk_api import VK
from api.auth.session_generator import generate_session_params
from api.serializers import *


def social_auth(user_data, request):
    try:
        username = request.POST['username']
    except MultiValueDictKeyError:
        return Response(
            {'error': 'user not found, register new by including username in request'},
            status=404
        )
    user = User.objects.filter(username=username).first()
    if user:
        return JsonResponse({'error': 'username already taken'}, status=400)
    user = User.objects.create_user(
        username,
        password=binascii.hexlify(os.urandom(10)).decode('utf-8'),
        first_name=user_data['first_name'],
        last_name=user_data['last_name']
    )

    if user_data['network'] is 'fb':
        user.fb_profile = user_data['user_id']
    elif user_data['network'] is 'vk':
        user.vk_profile = user_data['user_id']
    user.save()
    return Response(AuthResponseSerializer(generate_auth_response(user)).data)


# noinspection PyUnresolvedReferences
class SocialAuthView(APIView):
    permission_classes = (AllowAny,)

    def __init__(self, **kwargs):
        assert self.social_backend is not None, \
            "SocialAuthView must provide a `social_backend` field"
        assert self.user_profile_field is not None, \
            "SocialAuthView must provide a `user_profile_field` field"
        super().__init__(**kwargs)

    def post(self, request):
        token = request.POST.get('token')
        user_data = self.social_backend.get_user_data(token)
        user = User.objects.filter(**{self.user_profile_field: user_data['user_id']}).first()
        if user:
            return Response(AuthResponseSerializer(instance=generate_auth_response(user)).data)
        else:
            return social_auth(user_data, request)


class VKAuthView(SocialAuthView):
    user_profile_field = 'vk_profile'
    social_backend = VK()


class FBAuthView(SocialAuthView):
    user_profile_field = 'fb_profile'
    social_backend = FB()


def generate_auth_response(user):
    return {
        'user': user,
        'session': Session.objects.create(**generate_session_params(user)),
    }


class RefreshToken(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        refresh_token = request.POST.get('refresh_token')
        old_session = Session.objects.filter(refresh_token=refresh_token).first()
        if old_session is None:
            return Response({'error': 'invalid token'}, status=403)
        new_session = generate_auth_response(old_session.user)
        old_session.delete()
        return Response(AuthResponseSerializer(new_session).data)


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = (DjangoObjectPermissions,)
    serializers = {
        'DEFAULT': UserSerializer,
        'sign_up': SignUpSerializer,
        'sign_in': SignInSerializer,
    }

    # для нормального отображения в BrowsableAPIRenderer
    def get_serializer_class(self):
        return self.serializers.get(self.action, self.serializers['DEFAULT'])

    @list_route(methods=['post'], permission_classes=(AllowAny,))
    def sign_up(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.create_user(**serializer.data)
        return Response(
            AuthResponseSerializer(instance=generate_auth_response(user)).data,
            status=status.HTTP_201_CREATED
        )

    @list_route(methods=['post'], permission_classes=(AllowAny,))
    def sign_in(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(**serializer.data)
        if user:
            user.sessions.all().delete()
            return Response(AuthResponseSerializer(instance=generate_auth_response(user)).data)
        else:
            return Response({'error': 'wrong username or password'}, status=403)


class CompositionViewSet(mixins.CreateModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    queryset = Composition.objects.all()
    serializer_class = CompositionSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('band__members__user', 'band__members')


class InstrumentViewSet(mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):
    queryset = Instrument.objects.all()
    serializer_class = InstrumentSerializer


class BandMembersViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = BandMemberSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('band',)


class BandViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    queryset = Band.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'description')
    serializer_class = BandSerializer

    def create(self, request, *args, **kwargs):
        data = request.POST.copy()
        data['leader'] = request.user.id
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        band = serializer.save()
        return Response(self.serializer_class(band).data, status=status.HTTP_201_CREATED)
