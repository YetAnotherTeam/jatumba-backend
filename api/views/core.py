import json

from django.db import transaction
from rest_framework import status, viewsets, mixins, filters
from rest_framework.permissions import DjangoObjectPermissions
from rest_framework.response import Response

from api.filters import TrackHistoryFilter
from api.models import Composition, Member, Band, Track, TrackHistory, Sound
from api.serializers import CompositionSerializer, BandMemberSerializer, BandSerializer, \
    TrackSerializer, TrackHistorySerializer


class BandViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    permission_classes = (DjangoObjectPermissions,)
    queryset = Band.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'description')
    serializer_class = BandSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        band = serializer.save(leader=self.request.user)
        Member.objects.create(band=band, user=self.request.user)


class BandMembersViewSet(viewsets.ModelViewSet):
    permission_classes = (DjangoObjectPermissions,)
    queryset = Member.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('band',)
    serializer_class = BandMemberSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CompositionViewSet(mixins.CreateModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    queryset = Composition.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('band__members__user', 'band__members')
    serializer_class = CompositionSerializer


class TrackViewSet(viewsets.ModelViewSet):
    permission_classes = (DjangoObjectPermissions,)
    queryset = Track.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('composition',)
    serializer_class = TrackSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)

        composition = Composition.objects.get(id=data['composition'])
        membership = Member.objects.filter(user=request.user, band=composition.band).first()
        if membership is None:
            return Response({'error': 'you are not member of this band'}, status=403)

        if self.validate_track(data['track'], data['instrument']):
            track = serializer.save()
            TrackHistory.objects.create(track=track.track, track_key=track)
            return Response(self.serializer_class(track).data, status=status.HTTP_201_CREATED)
        return Response({'error': 'invalid sounds in track'}, status=400)

    def partial_update(self, request, *args, **kwargs):
        request_body = json.loads(request.body.decode('utf-8'))
        new_track = request_body['track']
        track = self.get_object()

        if self.validate_track(new_track, track.instrument_id):
            serializer = self.serializer_class(track, data={'track': new_track}, partial=True)
            serializer.is_valid(raise_exception=True)
            track = serializer.save()
            TrackHistory.objects.create(track=track.track, track_key=track,
                                        modified_by=request.user)
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


class TrackHistoryViewSet(mixins.RetrieveModelMixin,
                          mixins.ListModelMixin,
                          viewsets.GenericViewSet):
    queryset = TrackHistory.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = TrackHistoryFilter
    serializer_class = TrackHistorySerializer
