from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import user_passes_test
import snippets, views

urlpatterns = patterns('accounts.views',
	url(r'login/$', 'login'),
	url(r'logout/$', 'logout'),
	url(r'info/%s/$' % snippets.REG_USER_ID,
         views.UserView.as_view(), 
         name='user-info'
    ),
    url(r'admin/$', user_passes_test(lambda user: user.is_superuser)(views.AdminView.as_view())),
)