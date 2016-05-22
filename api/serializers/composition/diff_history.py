# noinspection PyAbstractClass
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.models import DiffCompositionVersion


# noinspection PyAbstractClass
class DiffHistorySerializer(serializers.Serializer):
    diff_composition_version = serializers.PrimaryKeyRelatedField(
        queryset=DiffCompositionVersion.objects.all()
    )

    def validate_diff_composition_version(self, diff_composition_version):
        if self.context['composition_id'] != diff_composition_version.composition_id:
            raise ValidationError('Wrong diff composition version.')
        return diff_composition_version
