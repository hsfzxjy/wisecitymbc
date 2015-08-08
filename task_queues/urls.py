from django.conf.urls import url, patterns, include

from .core import cache

urlpatterns = patterns('')
for pattern in cache.get_objects():
    urlpatterns += pattern
