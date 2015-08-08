from django.conf.urls import patterns, include, url

urlpatterns = patterns('file_storage.views',
    url(r'^uptoken/$', 'upload_token',),
	url(r'^download/(?P<file_id>\d+)/$', 'download', name = 'file.download'),
)
