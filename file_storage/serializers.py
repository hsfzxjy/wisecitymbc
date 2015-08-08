from rest_framework import serializers
from models import File

class FileSerializer(serializers.ModelSerializer):
        
    url = serializers.Field(source = 'url')
    file_name = serializers.Field(source = 'file_name')

    class Meta:
        model = File
        fields = ('created_time', 'name', 'url', 'content_type', 'sections', 'id', 'file_name')
        write_only = ('sections','content_type',)