# coding: utf-8
from __future__ import unicode_literals

from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from rest_framework.relations import RelatedField


# noinspection PyAbstractClass,PyCallingNonCallable
class DeserializePrimaryKeyRelatedField(RelatedField):
    default_error_messages = {
        'required': _('This field is required.'),
        'does_not_exist': _('Invalid pk "{pk_value}" - object does not exist.'),
        'incorrect_type': _('Incorrect type. Expected pk value, received {data_type}.'),
    }

    def __init__(self, **kwargs):
        self.serializer = kwargs.pop('serializer', None)
        self.serializer_params = kwargs.pop('serializer_params', dict())
        assert self.serializer is not None, (
            'DeserializePrimaryKeyRelatedField field must provide a `serializer` argument'
        )
        kwargs['style'] = {'base_template': 'input.html', 'input_type': 'numeric'}
        super(DeserializePrimaryKeyRelatedField, self).__init__(**kwargs)

    def use_pk_only_optimization(self):
        return False

    def to_internal_value(self, data):
        try:
            return self.get_queryset().get(pk=data)
        except ObjectDoesNotExist:
            self.fail('does_not_exist', pk_value=data)
        except (TypeError, ValueError):
            self.fail('incorrect_type', data_type=type(data).__name__)

    def to_representation(self, value):
        self.serializer_params['instance'] = value
        return self.serializer(**self.serializer_params).data
