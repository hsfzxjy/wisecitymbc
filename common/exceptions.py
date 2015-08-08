from django.http import HttpResponseRedirect
from rest_framework.views import exception_handler

def handle_403_exception(exception):
    response = exception_handler(exception)
    if response and response.status_code == 403 and not getattr(exception, 'is_api', False):
        return HttpResponseRedirect('/accounts/login/')
    return response
