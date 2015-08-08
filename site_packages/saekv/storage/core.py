from .fields import KVModel

__all__ = ['Field', 'ArrayField', 'DictField', 'NestedField', 'Model']

class Field(object):

    def __init__(self, default = None):
        self.default = default

    def get_default(self):
        default = self.default

        if callable(default):
            default = default()

        return default

class ArrayField(Field):

    def __init__(self):
        super(ArrayField, self).__init__([])

class DictField(Field):

    def __init__(self):
        super(DictField, self).__init__({})

class NestedField(Field):

    def __init__(self, model):
        self.foreign_model = model
        super(NestedField, self).__init__()

    def get_default(self):
        return self.foreign_model._get_default()

class Model(KVModel):

    def __getattribute__(self, key):
        attr = object.__getattribute__(self, key)
        if isinstance(attr, Field):
            raise AttributeError

        return attr

    @classmethod
    def _get_field_class(cls, key):
        field = getattr(cls, str(key), None)
        if isinstance(field, NestedField):
            return field.foreign_model

        return super(Model, cls)._get_field_class(key)

    @classmethod
    def _get_default(cls):
        field_tuples = []

        for name in dir(cls):
            attr = getattr(cls, name)
            if isinstance(attr, Field):
                field_tuples.append((name, attr))

        return {name: attr.get_default() for name, attr in field_tuples}