from django.conf.urls import patterns, include, url
from accounts.snippets import REG_CATEGORY
from .views import StatusListView

urlpatterns = patterns('articles.views',
    url(r'^{0}/$'.format(REG_CATEGORY), StatusListView.as_view()),
    url(r'^(\d+)/$', 'status_detail', name = 'status-detail'),
    url(r'^add/$', 'status_add', name = 'status-add'),
    url(r'^(\d+)/modify/$', 'status_modify', name = 'status-modify'),
)