from rest_framework.request import Request 
from django.template.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt

def task_queue_callback(func):

    @csrf_exempt
    def renderer(request, *args, **kwargs):

        func(Request(request), *args, **kwargs)

        return HttpResponse('')

    return renderer