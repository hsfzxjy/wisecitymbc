from rest_framework import serializers
from common.serializers import WritableRelatedField
from accounts.serializers import UserSerializer

from .models import Notice

class NoticeSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'content', 'title', 'has_read', 'created_time', 'notice_type', 'url')
        model = Notice