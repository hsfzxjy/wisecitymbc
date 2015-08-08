from django.http import HttpResponse, HttpResponseRedirect
from django.utils.encoding import iri_to_uri
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from datetime import datetime
from django.conf import settings
from django.http import Http404
import exceptions
import sys

#Paginate               

def getattrex(obj, field_name, default = None):
    for field in field_name.split('.'):
        try:
            obj = getattr(obj, field)
        except AttributeError:
            return default
    else:
        return obj

def getattrlazy(obj, field_name, default=None):
    return lambda: getattrex(obj, field_name, default)

def paginate(objects, objects_per_page = 20, page = 1):
    p = Paginator(objects, objects_per_page)
    try:
        objs = p.page(page)
    except (EmptyPage, InvalidPage):
        objs = p.page(p.num_pages)
    return objs
    
def paginate_by_request(objects, request, objects_per_page = 20):
    try:
        page = int(request.GET.get('page',1))
    except ValueError:
        page = 1
    try:
        objects_per_page = int(request.GET.get('limit','') or request.POST.get('limit',''))
    except:
        pass
    return paginate(objects, objects_per_page, page)
    
def paginate_to_dict(objects, request, objects_per_page = 20, ajax_by_request = True, is_ajax = True):
    page = paginate_by_request(objects, request, objects_per_page)
    if ajax_by_request:
        ajax = request.method == 'POST'
    else:
        ajax = is_ajax
    if not ajax:
        return {'objects': page}
    response = {'objects': page.object_list}
    response.update(get_attributes(page, ['has_next', 'has_previous',
         'number'], attr_name = ''))
    return response
    
#get object
def get_object_by_id(cls, id, raise_404 = False, method = ''):
    try:
        return cls.objects.get(id = int(id))
    except:
        if method:
            raise_404 = method == 'GET'
        if raise_404:
            raise Http404
        else:
            raise exceptions.ObjectNoFound
    
#GET&POST
def to_callable(object_name):
    if callable(object_name):
        return object_name
    splitter = object_name.rfind('.')
    try:
        module_name = object_name[:splitter] if splitter>=0 else ''
        method_name = object_name[splitter+1:]
        if splitter >= 0:
            method = getattr(__import__(module_name, fromlist = [1]), method_name)
        else:
            method = getattr(sys.modules[__name__], method_name)
        print method 
        return method
    except ImportError:
        raise exceptions.MethodError, 'Module name error.'
    except AttributeError:
        raise exceptions.MethodError, 'Method name error.'

def views_splitter(request, **kw_args):
    get = kw_args.pop('GET', '')
    post = kw_args.pop('POST', '')
    if get and request.method == 'GET':
        return to_callable(get)(request, **kw_args)
    elif post and request.method == 'POST':
        return to_callable(post)(request, **kw_args)
    else:
        raise exceptions.MethodError
        
def verify_user(request, users):
    try:
        iter(users)
    except:
        users = [users]
    if not filter(lambda user: request.user == user, users):
        raise exceptions.AccessDenied