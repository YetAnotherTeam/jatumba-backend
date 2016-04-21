from django.db.transaction import atomic
from rest_framework import serializers


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


class ObjectListSerializer(serializers.ListSerializer):
    @atomic
    def create(self, validated_data):
        """
        Такой create работает для объектов у которых нет related полей в validated_data
        """
        # Хак, чтобы не переопределять сериализаторы для чтения и записи
        validated_data = self.remove_ids(validated_data)
        Model = self.child.Meta.model
        objs = [Model(**item) for item in validated_data]
        return Model.objects.bulk_create(objs)

    @atomic
    def update(self, db_objects, validated_data):
        ret = []
        db_object_mapping = {db_object.id: db_object for db_object in db_objects}
        data_ids = {item.get('id') for item in validated_data if item.get('id') is not None}
        for db_object_id, db_object in db_object_mapping.items():
            if db_object_id not in data_ids:
                db_object.delete()

        for item in validated_data:
            item_id = item.get('id')
            if item_id is None:
                # Новый id - новый объект
                ret.append(self.child.create(item))
            elif item_id not in db_object_mapping:
                # В базе нет объектов с id, которые пришли с фронта, значит игнорируем id и
                # создаем новые.
                item.pop('id')
                ret.append(self.child.create(item))
            else:
                # В базе есть элементы с таким id - обновляем существующие элементы
                ret.append(self.child.update(db_object_mapping.get(item_id), item))
        return ret

    def remove_ids(self, obj):
        return self.remove_keys(obj, ('id',))

    def remove_keys(self, obj, rubbish):
        """
        Рекурсивно удаляет ключи из obj
        """
        if isinstance(obj, dict):
            obj = {key: self.remove_keys(value, rubbish)
                   for key, value in obj.items()
                   if key not in rubbish}
        elif isinstance(obj, list):
            obj = [self.remove_keys(item, rubbish) for item in obj if item not in rubbish]
        return obj
