from .views import finance_viewsets
import views

routers  = [
    (r'^finance-data/logs(/(?P<key>\w+))?', views.DataLogAPIViewSet),
    (r'^finance-year/$', views.FinanceYearAPIView),
    (r'^finance-data/$', views.finance_data),
    (r'^finance-extra-fields/$', views.finance_extra_chart_fields)
]

for model_name, viewsets in finance_viewsets.iteritems():
    routers.append((
        r'^%s' % model_name,
        viewsets[0]
    ))
    routers.append((
        r'^%s/(?P<finance_pk>\d+)/logs' % model_name,
        viewsets[1]
    ))