from django.db.transaction import atomic
from rest_framework import viewsets, filters, status
from rest_framework.permissions import DjangoObjectPermissions
from rest_framework.response import Response

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

    def create(self, request, *args, **kwargs):
        request.data['user'] = self.request.user.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @atomic
    def perform_create(self, serializer):
        member = serializer.save()
        member.band.group.user_set.add(self.request.user)

    @atomic
    def perform_destroy(self, instance):
        user = self.request.data['user']
        instance.band.group.user_set.add(user)
        instance.delete()
