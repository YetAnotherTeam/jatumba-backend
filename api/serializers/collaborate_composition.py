from rest_framework import serializers

from api.models import CollaborateTrackDiff, CollaborateTrackSnapshot


class CollaborateTrackDiffSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollaborateTrackDiff
        fields = '__all__'


class CollaborateTrackSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollaborateTrackSnapshot
        fields = '__all__'
