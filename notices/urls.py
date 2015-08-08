from django.conf.urls import patterns, include, url
import views

urlpatterns = patterns('notices.views',
    url(r'^', include(views.NoticeViewSet.get_urls())),
)