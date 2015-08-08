from django.conf.urls import url, patterns, include
from .constants import finance_categories
import views

url_reg = r'(?P<category>{0})'.format('|'.join(finance_categories))

urlpatterns = (
    url(r'^$', views.FinanceIndexView.as_view()),
    url(r'^{0}/$'.format(url_reg), views.FinanceListView.as_view()),
    url(r'^{0}/(?P<pk>\d+)/$'.format(url_reg), views.FinanceDetailView.as_view()),
)