from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, decorators, response, views
import models, serializers
from .constants import finance_categories
from django.views.generic import TemplateView
from common.rest.mixins import ListCacheMixin

def create_viewset(model_name):

    model_class = models.get_finance_class(model_name)
    log_model_class = models.get_log_class(model_name)

    class FinanceAPIViewSet(viewsets.ReadOnlyModelViewSet, ListCacheMixin):

        model = model_class
        serializer_class = serializers.get_serializer_class(model_class)

    class FinanceLogAPIViewSet(viewsets.ReadOnlyModelViewSet, ListCacheMixin):

        model = log_model_class
        serializer_class = serializers.get_log_serializer_class(log_model_class)

        def get_queryset(self):
            pk = int(self.kwargs['finance_pk'])
            return log_model_class.objects.filter(finance_object = pk)

    return (FinanceAPIViewSet, FinanceLogAPIViewSet)

finance_viewsets = {model_name: create_viewset(model_name) for model_name in finance_categories}

class FinanceViewBase(object):

    def _get_context(self):
        category = self.kwargs['category']
        model = models.get_finance_class(category)
        return {
            'category': category,
            'model': model,
            'need_log': model.need_log
        }

class FinanceIndexView(TemplateView):

    template_name = 'finance/index.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response(context = {
            'models': {
                model_name: models.get_finance_class(model_name)
                for model_name in finance_categories
            }
        })

class FinanceListView(TemplateView, FinanceViewBase):
    
    template_name = 'finance/list.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response(context = self._get_context())

class FinanceDetailView(TemplateView, FinanceViewBase):
    
    template_name = 'finance/detail.html'

    def get(self, request, *args, **kwargs):
        model_class = models.get_finance_class(self.kwargs['category'])
        finance_object = get_object_or_404(model_class, pk = int(self.kwargs['pk']))
        context = self._get_context()
        context.update({
            'finance_object': finance_object,
        })
        return self.render_to_response(context = context)

class DataLogAPIViewSet(viewsets.ReadOnlyModelViewSet):

    model = models.DataLog
    serializer_class = serializers.DataLogSerializer

    def get_queryset(self):
        key = self.kwargs.get('key', 'index')

        return get_object_or_404(models.ExtraData, key = key).logs.all()

from common.rest.decorators import cache_view_func

@cache_view_func
@decorators.api_view(['GET'])
def finance_extra_chart_fields(request, *args, **kwargs):
    extra_fields = {
        model_name: models.get_log_class(model_name).get_extra_chart_fields()
        for model_name in finance_categories
    }

    return response.Response(extra_fields)

@cache_view_func
@decorators.api_view(['GET'])
def finance_data(request, *args, **kwargs):
    object_list = models.ExtraData.objects.filter(display_on_home_page = True)
    data = serializers.ExtraDataSerializer(object_list).data 

    return response.Response(data)

class FinanceYearAPIView(views.APIView):

    def post(self, request, *args, **kwargs):
        action = request.REQUEST.get('action', '')
        if action in ('reset', 'inc'):
            self.object = models.ExtraData.objects.get(key = 'year')
            self.post_year = self.object.decimal_value
            getattr(self, action)()
            from .signals import finance_year_changed
            finance_year_changed.send(sender = self, post_year = self.post_year, current_year = self.current_year)

        return response.Response('ok')

    def reset(self):
        from datetime import datetime 
        self.current_year = self.object.decimal_value = datetime.now().year
        self.object.save()

    def inc(self):
        self.current_year = self.object.decimal_value = self.post_year + 1
        self.object.save()