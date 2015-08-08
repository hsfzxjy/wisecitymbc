#encoding=utf8
import common
from common.utils import get_object_by_id, HttpResponse
from django.shortcuts import render_to_response
from .models import User
from django.contrib import auth
from django.http import HttpResponseRedirect
import models, serializers

from rest_framework import views, generics, viewsets, permissions, status, renderers
from rest_framework.decorators import *
from rest_framework.response import Response

from django.views.generic import TemplateView 
from .mixins import UserMixin

class UserAPIViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.UserSerializer
    model = models.User
    filter_fields = ('category', )

    def get_object(self):
        pk = self.kwargs.get('pk', None)
        if pk == 'me':
            return self.request.user
        else:
            return super(UserAPIViewSet, self).get_object()

@api_view(['GET', 'POST'])
@permission_classes([])
@renderer_classes([renderers.TemplateHTMLRenderer, renderers.JSONRenderer])
def login(request, *args, **kwargs):
    redirect_to = request.GET.get('next', '') or request.META.get('HTTP_REFERER', '') or '/'

    if request.method == 'GET':
        return Response({
            'redirect_to': redirect_to
        }, template_name = 'accounts/login.html')

    username = request.DATA.get('username', '')
    password = request.DATA.get('password', '')
    user = auth.authenticate(username = username, password = password)   
    if user:
        auth.login(request, user)
        return Response({'status': 'OK'})
    else:
        return Response({'status': 'error'})

def logout(request):
    auth.logout(request)
    return common.utils.HttpResponseRedirect("/")

from django.contrib import messages

class UserView(TemplateView, UserMixin):

    template_name = 'accounts/info.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response(context = self.render_context(context = {
                'active': 'home'
            }))

    def post(self, request, *args, **kwargs):
        description = request.POST.get('description', '')
        request.user.description = description
        request.user.save()
        messages.info(request, '修改成功！')

        return HttpResponseRedirect('/accounts/info/me/')


from .utils import import_users_from_excel

class AdminView(TemplateView, UserMixin):

    template_name = 'accounts/admin.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response(context = self.render_context(
            context = {'active': 'admin'},
            user_id = 'me'
        ))

    def post(self, request, *args, **kwargs):
        results = import_users_from_excel(request)

        return self.render_to_response(context = self.render_context(
            context = {'user_results': results, 'active': 'admin'},
            user_id = 'me'
        ))