#encoding=utf8
from rest_framework import viewsets, mixins, permissions, exceptions
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.decorators import action, renderer_classes, api_view, permission_classes
from rest_framework.response import Response

from serializers import CommentSerializer, StatusSerializer
from .models import Status, Comment
from django.db.models import Count
from django.shortcuts import get_object_or_404

from common.rest.permissions import own_object_permission, custom_perm, custom_perms_map

from common.rest.mixins import ListCacheMixin

class StatusAPIViewSet(viewsets.ModelViewSet, ListCacheMixin):

    serializer_class = StatusSerializer
    model = Status
    filter_fields = ('status_type',)

    def get_queryset(self):
        queryset = Status.objects.annotate(comment_count = Count('comments'))
        return queryset

    def create(self, request, *args, **kwargs):
        response = super(StatusAPIViewSet, self).create(request, *args, **kwargs)

        if hasattr(self, 'object'):
            from .signals import status_posted
            status_posted.send(sender = self.object, data = request.DATA)

        return response

class CommentAPIViewSet(viewsets.ModelViewSet):
    
    serializer_class = CommentSerializer
    permission_classes = (
        custom_perms_map({
            'POST': ['articles.comment_status']
        }),
    )
    model = Comment

    def get_queryset(self):
        status_id = int(self.kwargs['status_id'])
        return get_object_or_404(
            Status,
            pk = status_id
        ).comments.all()

from django.views.generic import TemplateView

class StatusListView(TemplateView):

    template_name = 'articles/status/list.html'

    def get_navbar_items(self, category):
        items_tuple = (('', u'总览'),) + Status.STATUS_TYPE_MAP[category]

        return [{
            'name': item[1],
            'type': item[0],
            'url': '?type={0}'.format(item[0]) if item[0] else '?'
        } for item in items_tuple]

    def get(self, request, *args, **kwargs):

        category = self.kwargs['category']

        return self.render_to_response(context = {
            'type': request.GET.get('type', ''),
            'category': category,
            'navbar_items': self.get_navbar_items(category) 
        })

@api_view(['GET'])
@renderer_classes([TemplateHTMLRenderer])
def status_detail(request, id):
    status_object = get_object_or_404(Status, pk = id)
    status_object.incr_view_times()

    from finance.models import PlayerDataLog
    return Response({
        'status': status_object,
        'player_data': PlayerDataLog.objects.filter(status = status_object)
    }, template_name = 'articles/status/detail.html')

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@renderer_classes([TemplateHTMLRenderer])
def status_add(request):
    return Response({}, template_name = 'articles/status/write.html')

@api_view(['GET'])
@renderer_classes([TemplateHTMLRenderer])
def status_modify(request, id):
    status = get_object_or_404(Status, pk = id)
    if request.user != status.author:
        raise exceptions.PermissionDenied(is_api = False)
    return Response({
        'status_object': status,
    }, template_name = 'articles/status/write.html')

@api_view(['GET']) 
@renderer_classes([TemplateHTMLRenderer])
def comment_detail(request, *args, **kwargs):
    return Response({}, template_name = 'articles/comment/detail.html')
