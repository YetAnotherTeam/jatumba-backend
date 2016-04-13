from rest_framework import filters

from api.models import TrackHistory


class TrackHistoryFilter(filters.FilterSet):
    track = filters.django_filters.NumberFilter(name='track_key', required=True)

    class Meta:
        model = TrackHistory
        fields = ('track',)
