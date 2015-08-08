from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^$',         'site_config.views.index'),
    url(r'^why-not-ie/$', TemplateView.as_view(template_name = 'contents/why-not-ie.html')),
    url(r'^map/$', TemplateView.as_view(template_name = 'map.html')),
    url(r'^admin/',    include(admin.site.urls)),
    url(r'^api/', include('api.urls')),
    url(r'^files/', include('files.urls')),
    url(r'^storage/', include('file_storage.urls')),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^articles/', include('articles.urls')),
    url(r'^finance/',  include('finance.urls')),
    url(r'^notices',  include('notices.urls')),
    url(r'^task-queues/', include('task_queues.urls')),
)