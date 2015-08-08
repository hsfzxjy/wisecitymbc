from django.contrib import admin
from .models import SharedFile

class SharedFileAdmin(admin.ModelAdmin):

    readonly_fields = ('uploader', 'file')

    def has_add_permission(self, *args, **kwargs):
        return False

admin.site.register(SharedFile, SharedFileAdmin)