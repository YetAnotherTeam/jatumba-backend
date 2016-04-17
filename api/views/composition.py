import ujson

from rest_framework import mixins, viewsets, filters, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.models import Composition, Track, Sound
from api.serializers import CompositionSerializer, TrackSerializer


class CompositionViewSet(mixins.CreateModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    queryset = Composition.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('band__members__user', 'band__members')
    serializer_class = CompositionSerializer


class TrackViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = Track.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('composition',)
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