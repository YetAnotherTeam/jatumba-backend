from rest_framework import mixins, viewsets

from api.models import Instrument
from api.serializers import InstrumentListItemSerializer


class InstrumentViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Instrument.objects.order_by('name').prefetch_related('sounds')
    serializer_class = InstrumentListItemSerializer
    pagination_class = None
