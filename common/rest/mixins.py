from django.core.cache import cache 
from django.http import HttpResponse
from rest_framework.mixins import ListModelMixin
from .decorators import cache_view_method

class ListCacheMixin(ListModelMixin):

    @cache_view_method
    def list(self, request, *args, **kwargs):
        return super(ListCacheMixin, self).list(request, *args, **kwargs)