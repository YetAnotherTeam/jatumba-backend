class DynamicFieldsMixin(object):
    def __init__(self, *args, **kwargs):
        initial_fields = kwargs.pop('required_fields', None)

        # Поля, которые заменяются при создании
        replace_fields = kwargs.pop('replace_fields', None)
        if replace_fields is not None:
            for field_name, substitute_field in replace_fields.items():
                self.fields[field_name] = substitute_field

        super(DynamicFieldsMixin, self).__init__(*args, **kwargs)

        # Выбор необходимых полей
        allowed = self._get_allowed_fields(initial_fields)
        if allowed is not None:
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def _get_allowed_fields(self, initial_fields):
        """
        Возвращает список полей, которые формируются из required_fields в kwargs и поля
        required_fields
        """
        required_fields = getattr(self, 'required_fields', None)
        allowed = None
        if required_fields is not None:
            allowed = set(required_fields)
        if initial_fields is not None:
            if allowed is not None:
                allowed &= set(initial_fields)
            else:
                allowed = set(initial_fields)
        return allowed