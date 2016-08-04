from django.db.models import Count
from django.db.models.expressions import RawSQL
from django.db.transaction import atomic
from rest_framework import filters, status, viewsets
from rest_framework.permissions import DjangoObjectPermissions
from rest_framework.response import Response

from api.models import Band, Leader, Member
from api.serializers import BandSerializer, MemberSerializer


class BandViewSet(viewsets.ModelViewSet):
    permission_classes = (DjangoObjectPermissions,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('@name', '@description')
    serializer_class = BandSerializer

    def get_queryset(self):
        return (
            Band.objects
            .annotate(
                user_joined=RawSQL(
                    'SELECT 1 FROM api_member '
                    'WHERE api_member.band_id = api_band.id AND api_member.user_id = %s '
                    'LIMIT 1',
                    (self.request.user.id,)
                )
            )
            .annotate(compositions_count=Count('compositions', distinct=True))
            .annotate(members_count=Count('members', distinct=True))
            .select_related('leader__member__user')
        )

    @atomic
    def perform_create(self, serializer):
        user = self.request.user
        band = serializer.save()
        member = Member.objects.create(band=band, user=user)
        Leader.objects.create(band=band, member=member)


class MemberViewSet(viewsets.ModelViewSet):
    permission_classes = (DjangoObjectPermissions,)
    queryset = Member.objects.select_related('user', 'band')
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('band',)
    serializer_class = MemberSerializer

    def create(self, request, *args, **kwargs):
        data = dict(request.data)
        data['user'] = self.request.user.id
        serializer = self.get_serializer(data=data)
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
