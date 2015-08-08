from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect
from common.decorators import render_to
from common.shortcuts import redirect_back
from rest_framework import viewsets, mixins, decorators, renderers, response

from .models import Notice
from .serializers import NoticeSerializer

from accounts.mixins import UserMixin

@render_to('notices/index.html')
def index(request):
    return {'object': request.user}

class NoticeBaseViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = NoticeSerializer
    model = Notice

    def get_queryset(self):
        return Notice.objects.filter(user = self.request.user)

class NoticeViewSet(NoticeBaseViewSet, UserMixin):

    renderer_classes = (renderers.TemplateHTMLRenderer,)
    template_name_mapping = {
        'list': 'notices/index.html'
    }
    context_name_mapping = {
        'list': 'notices'
    }

    def preprocess_data(self, data, *args, **kwargs):
        context = super(NoticeViewSet, self).preprocess_data(data, *args, **kwargs)
        context.update({'active': 'notices'})
        data = self.render_context(
            context = context,
            user_id = 'me'
        )

        return data

    @decorators.view_action(['POST'])
    def mark_read(self, request, *args, **kwargs):
        id_list = request.DATA.getlist('ids', [])
        self.get_queryset().filter(pk__in = id_list).update(has_read = True)
        return redirect_back(request)

    @decorators.action(['GET'])
    def view(self, reuqest, *args, **kwargs):
        obj = self.get_object()
        if not obj.notice_type == 'link' or not obj.url:
            raise Http404

        obj.has_read = True
        obj.save()

        return HttpResponseRedirect(obj.url)


class NoticeAPIViewSet(NoticeBaseViewSet, mixins.DestroyModelMixin):
    
    @decorators.action(['POST'])
    def mark_read(self, request, *args, **kwargs):
        notice = self.get_object()
        if not notice.has_read:
            notice.has_read = True
            notice.save()
        return response.Response({})