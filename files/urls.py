from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from .views import UploadView
from django.contrib.auth.decorators import permission_required as pr

urlpatterns = patterns('files.urls',

    url(
        r'^$', 
        TemplateView.as_view(template_name = 'files/index.html'), 
        name = 'files-index'
    ),
    url(
        r'^upload/$', 
        pr('files.manage_file')(UploadView.as_view(template_name = 'files/upload.html')), 
        name = 'files-upload'
    )
)