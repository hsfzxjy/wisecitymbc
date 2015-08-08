#encoding=utf8
from django.http import Http404
from django.shortcuts import get_object_or_404

from .models import User

class UserMixin(object):

    def get_tab_lists(self, is_me):
        if not is_me:
            return {}

        context = [
            ('home', '主页', '/accounts/info/me'),
            ('notices', '通知', '/notices/'),
        ]

        if self.request.user.is_superuser:
            context.append(('admin', '管理', '/accounts/admin/'))

        return (
            {
                'name': item[0],
                'title': item[1],
                'url': item[2]
            } for item in context
        )


        return context

    def render_context(self, user_id = '', context = None, object_name = 'user_object', active = ''):
        context = context or {}
        user_id = user_id or self.kwargs.get('user_id', '')

        if user_id == 'me':
            user = self.request.user
        else:
            user = get_object_or_404(User, pk = user_id)

        if not user.is_authenticated():
            raise Http404

        result = {
            object_name: user,
            'active': active,
            'tab_lists': self.get_tab_lists(user == self.request.user)
        }

        result.update(context)

        return result
