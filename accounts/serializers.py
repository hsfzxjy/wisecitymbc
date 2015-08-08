from rest_framework import serializers
from .models import User
from rest_framework.reverse import reverse

class UserSerializer(serializers.ModelSerializer):
    """serializer for `User` model."""

    url = serializers.Field('url')
    a_tag = serializers.Field('a_tag')

    class Meta:
        model = User
        fields = ('id', 'nickname', 'username','url', 'a_tag')