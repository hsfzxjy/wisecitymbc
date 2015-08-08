from django.contrib import admin
from .models import Status, Comment
from django.db import models
from .forms import StatusChangeForm
from django.utils.safestring import mark_safe
from django.utils.html import format_html

class StatusAdmin(admin.ModelAdmin):

    list_display = ('title', 'created_time')
    date_hierarchy = 'created_time'
    readonly_fields = ('author',)
    exclude = ('view_times',)
    form = StatusChangeForm
    fieldsets = (
        (None, {
            'fields': (
                'author',
                'title',
                'body_text',
                'attachments'
            )
        }),
    )

    def has_add_permission(self, request):
        return False

class CommentAdmin(admin.ModelAdmin):
    
    list_display = ('shorten', 'status', 'author', 'created_time',)
    readonly_fields = ('author', 'status', 'created_time', 'body_text')

    def get_queryset(self, request):
        queryset = Comment.objects.all()

        if request.user.is_superuser:
            return queryset

        return queryset.filter(status__author = request.user)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, *args):
        return True

    def has_delete_permission(self, request, obj = None):
        return request.user.is_staff or \
            obj.status.author == request.user

admin.site.register(Status, StatusAdmin)
admin.site.register(Comment, CommentAdmin)