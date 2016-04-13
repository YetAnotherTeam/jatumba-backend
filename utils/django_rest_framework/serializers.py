class DynamicFieldsMixin(object):
    def __init__(self, *args, **kwargs):
        fields = getattr(self, 'required_fields', None)
        super(DynamicFieldsMixin, self).__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)