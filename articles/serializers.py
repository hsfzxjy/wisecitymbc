from rest_framework import serializers, reverse
from .models import Status, Comment
from common.serializers import WritableRelatedField
from accounts.serializers import UserSerializer

class StatusSerializer(serializers.ModelSerializer):
    """serializer for `Status` model"""

    url = serializers.Field('url')
    comment_count = serializers.SerializerMethodField('get_comment_count')
    author = WritableRelatedField(serializer_class = UserSerializer)

    def get_comment_count(self, obj):
        if hasattr(obj, 'comment_count'):
            return obj.comment_count

        return obj.comments.all().count()

    class Meta:
        model = Status

class CommentSerializer(serializers.ModelSerializer):

    author = WritableRelatedField(serializer_class = UserSerializer)

    class Meta:
        model = Comment
        