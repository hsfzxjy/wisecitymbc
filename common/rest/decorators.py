from django.utils.decorators import method_decorator
from django.core.cache import cache 
from django.http import HttpResponse

def cache_view_func(func):

    def wrapper(request, *args, **kwargs):
        key = request.method + request.META['PATH_INFO'] + request.META['QUERY_STRING']
        content = cache.get(key)

        if content is None:
            response = func(request, *args, **kwargs)
            cache.set(key, response.rendered_content, 30)
            return response 
        else:
            return HttpResponse(content)

    return wrapper

def cache_view_method(func):

    def wrapper(self, request, *args, **kwargs):
        key = request.method + request.META['PATH_INFO'] + request.META['QUERY_STRING']
        content = cache.get(key)

        if content is None:
            response = func(self, request, *args, **kwargs)
            self.finalize_response(request, response, *args, **kwargs)
            cache.set(key, response.rendered_content, 30)
            return response 
        else:
            return HttpResponse(content)

    return wrapper