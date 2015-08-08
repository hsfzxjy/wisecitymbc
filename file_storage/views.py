from models import File
from serializers import FileSerializer
from django.http import StreamingHttpResponse
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from datetime import datetime
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.conf import settings

@api_view(['GET'])
def upload_token(request):
    from .qiniu_utils import auth
    token = auth.upload_token(settings.QINIU.get('bucket_name', ''))
    return Response({
        'uptoken': token
    })

def download(request, file_id):
    file = get_object_or_404(File, pk = file_id)
    storage = default_storage

    def generate_file():
        for section in file.sections:
            yield default_storage.open(section).read()

    response = StreamingHttpResponse(generate_file(), file.content_type)
    response['Content-Disposition'] = 'attachment; filename="%s"' % file.name

    return response

class FileAPIViewSet(ModelViewSet):

    model = File
    serializer_class = FileSerializer
    permission_classes = [] 
    
    def create(self, request, *args, **kwargs):

        if 'file' in request.FILES:
            uploaded_file = request.FILES['file']
            extra = {
                'name': uploaded_file.name,
                'sections': uploaded_file.sections,
                'content_type': uploaded_file.content_type,
                'upload_type': 'normal',
            }
        else:
            extra = {}

        print request.DATA

        kwargs.update(extra)

        res = super(FileAPIViewSet, self).create(request,  *args, **kwargs)

        return res