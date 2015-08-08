from rest_framework import serializers
from .models import SharedFile
from common.serializers import WritableRelatedField
from accounts.serializers import UserSerializer
from file_storage.serializers import FileSerializer

class SharedFileSerializer(serializers.ModelSerializer):

    created_time = serializers.DateTimeField(source = 'file.created_time')
    uploader = WritableRelatedField(serializer_class = UserSerializer)
    file = FileSerializer(read_only = True)

    class Meta:
        model = SharedFile