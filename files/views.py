from django.views.generic import TemplateView
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse

from .serializers import SharedFileSerializer
from .models import SharedFile

from rest_framework import viewsets, mixins

class SharedFileAPIViewSet(viewsets.ReadOnlyModelViewSet, mixins.DestroyModelMixin):

    model = SharedFile
    serializer_class = SharedFileSerializer

    def get_queryset(self):
        return SharedFile.objects.select_related('uploader', 'file')

class UploadView(TemplateView):

    def post(self, request, *args, **kwargs):
        file_ids = request.POST.getlist('files', [])

        SharedFile.objects.multi_create(request.user, file_ids)

        return HttpResponseRedirect(reverse('files-index'))