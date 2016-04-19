from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from api.models import Instrument
from api.serializers import InstrumentSerializer


class InstrumentViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Instrument.objects.all()
    serializer_class = InstrumentSerializer
