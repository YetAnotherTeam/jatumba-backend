from rest_framework import viewsets, mixins

from api.models import Instrument
from api.serializers import InstrumentSerializer


class InstrumentViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Instrument.objects.all()
    serializer_class = InstrumentSerializer
    pagination_class = None
