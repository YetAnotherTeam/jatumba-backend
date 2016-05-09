from django.db.transaction import atomic
from rest_framework import viewsets, filters
from rest_framework.permissions import DjangoObjectPermissions

from api.models import Band, Member, Leader
from api.serializers import BandSerializer, MemberSerializer


class BandViewSet(viewsets.ModelViewSet):
    permission_classes = (DjangoObjectPermissions,)
    queryset = Band.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'description')
    serializer_class = BandSerializer

    @atomic
    def perform_create(self, serializer):
        user = self.request.user
        band = serializer.save()
        member = Member.objects.create(band=band, user=user)
        Leader.objects.create(band=band, member=member)


class MemberViewSet(viewsets.ModelViewSet):
    permission_classes = (DjangoObjectPermissions,)
    queryset = Member.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('band',)
    serializer_class = MemberSerializer

    @atomic
    def perform_create(self, serializer):
        user = self.request.data['user']
        member = serializer.save(user=user)
        member.band.group.user_set.add(user)

    @atomic
    def perform_destroy(self, instance):
        user = self.request.data['user']
        instance.band.group.user_set.add(user)
        instance.delete()
