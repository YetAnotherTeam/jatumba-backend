import ujson

from django.contrib.auth import get_user_model
from rest_framework import mixins, viewsets, filters, status
from rest_framework.decorators import detail_route
from rest_framework.permissions import AllowAny, DjangoObjectPermissions
from rest_framework.response import Response

from api.models import Composition, Track, Sound, CompositionVersion, atomic, Fork
from api.serializers import (
    CompositionSerializer, TrackSerializer, CompositionVersionSerializer,
    ForkCreateSerializer, CompositionListItemSerializer, CompositionRetrieveSerializer
)

User = get_user_model()


class CompositionViewSet(viewsets.ModelViewSet):
    queryset = Composition.objects.all()
    permission_classes = (DjangoObjectPermissions,)
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('band__members__user', 'band__members', 'band')
    serializers = {
        'DEFAULT': CompositionSerializer,
        'retrieve': CompositionRetrieveSerializer,
        'list': CompositionListItemSerializer
    }

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.serializers['DEFAULT'])

    @atomic
    def perform_create(self, serializer):
        composition = serializer.save()
        CompositionVersion.objects.create(composition=composition, author=self.request.user)
        composition.assign_perms()


class CompositionVersionViewSet(mixins.CreateModelMixin,
                                mixins.RetrieveModelMixin,
                                mixins.UpdateModelMixin,
                                mixins.ListModelMixin,
                                viewsets.GenericViewSet):
    queryset = CompositionVersion.objects.all()
    serializers = {
        'DEFAULT': CompositionVersionSerializer
    }

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.serializers['DEFAULT'])

    @detail_route(methods=('post',))
    def rollback(self, request, pk=None):
        composition_version = self.get_object()
        (CompositionVersion
         .objects
         .filter(id__gt=composition_version.id, composition=composition_version.composition)
         .delete())
        serializer = self.get_serializer(composition_version)
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


class ForkViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    queryset = Fork.objects.all()

    serializers = {
        'DEFAULT': ForkCreateSerializer,
    }

    def get_serializer_class(self):
        return self.serializers.get(self.action, self.serializers['DEFAULT'])

    @atomic
    def perform_create(self, serializer):
        fork = serializer.save()
        fork.composition.assign_perms()


class TrackViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = Track.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    serializer_class = TrackSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)

        if self.validate_track(data['track'], data['instrument']):
            track = serializer.save()
            return Response(self.serializer_class(track).data, status=status.HTTP_201_CREATED)
        return Response({'error': 'invalid sounds in track'}, status=400)

    def partial_update(self, request, *args, **kwargs):
        request_body = ujson.loads(request.body.decode('utf-8'))
        new_track = request_body['track']
        track = self.get_object()

        if self.validate_track(new_track, track.instrument_id):
            serializer = self.serializer_class(track, data={'track': new_track}, partial=True)
            serializer.is_valid(raise_exception=True)
            track = serializer.save()
            return Response(self.serializer_class(track).data, status=status.HTTP_201_CREATED)
        return Response({'error': 'invalid sounds in track'}, status=400)

    def validate_track(self, track, instrument_id):
        sounds = Sound.objects.filter(instrument_id=instrument_id).values_list("name", flat=True)
        validation_flag = True
        for block in track:
            for sound in block:
                if sound not in sounds and sound != '0':
                    validation_flag = False
        return validation_flag
