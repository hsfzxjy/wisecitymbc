from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from copy import deepcopy
from .mixins import SendNoticeModelMixin

class Notice(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name = 'notices')
    title = models.CharField(max_length = 255)
    content = models.TextField()
    has_read = models.BooleanField(default = False)
    created_time  = models.DateTimeField(auto_now_add=True)

    related_object_type = models.ForeignKey(ContentType, null = True)
    related_object_id   = models.PositiveIntegerField(null = True)
    related_object      = GenericForeignKey('related_object_type', 'related_object_id')

    url = models.URLField()
    notice_type = models.CharField(max_length = 20, choices = (
        ('invoke', 'Invoke the callback URL.'),
        ('link', 'Provide a link for user.'),
    ), default = 'link')

    class Meta:
        ordering = ('has_read', '-created_time')

class NoticeDispatcher(object):

    def __init__(self, model, default = {}):
        if not issubclass(model, SendNoticeModelMixin):
            raise TypeError('The `model` must be a subclass of  `SendNoticeModelMixin`.')
        self.__model = model
        self.__default = {}
        self.__default.update(default)

    def send(self, *args, **kwargs):
        klass = Notice

        title = self.__model.generate_title(*args, **kwargs) 
        content = self.__model.generate_content(*args, **kwargs) 
        url = self.__model.generate_url(*args, **kwargs)
        user = self.__model.generate_user(*args, **kwargs)

        valid_keys_set = set(kwargs.iterkeys()) & \
            set(field.name for field in klass._meta.fields)

        params = deepcopy(self.__default)
        params.update({key: kwargs[key] for key in valid_keys_set})
        params.update({
            'title': title,
            'content': content,
            'url': url,
        })

        results = []
        try:
            iter(user)
        except:
            user = (user,)

        for _user in user:
            params['user'] = _user
            notice = klass(*args, **params)
            notice.save()
            results.append(notice)

        return results