from rest_framework.relations import PrimaryKeyRelatedField

class WritableRelatedField(PrimaryKeyRelatedField):

    def __init__(self, *args, **kwargs):
        self.serializer_class = kwargs.pop('serializer_class', None)
        super(WritableRelatedField, self).__init__(*args, **kwargs)
        
    def field_to_native(self, obj, field_name):
        field = getattr(obj, field_name)
        if self.many:
            field = field.all()

        return self.serializer_class(field, many = self.many).data