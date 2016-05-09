from rest_framework import viewsets, mixins

from api.models import Instrument
from api.serializers import InstrumentListItemSerializer


class InstrumentViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Instrument.objects.all()
    serializer_class = InstrumentListItemSerializer
    pagination_class = None
