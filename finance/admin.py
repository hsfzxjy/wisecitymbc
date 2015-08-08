from django.contrib import admin
from .models import *
from .constants import finance_categories

def get_readonly_fields(model):
    return filter(lambda x: not x.endswith('_id'), model._meta.get_all_field_names())

class ReallyDeleteAdmin(admin.ModelAdmin):

    actions = ['really_delete_selected']

    def get_actions(self, request):
        actions = super(ReallyDeleteAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def really_delete_selected(self, request, queryset):
        for obj in queryset:
            obj.delete()

        if queryset.count() == 1:
            message_bit = "1 photoblog entry was"
        else:
            message_bit = "%s photoblog entries were" % queryset.count()
        self.message_user(request, "%s successfully deleted." % message_bit)

    really_delete_selected.short_description = "Delete selected entries"



def register(model_name):

    model_class = get_finance_class(model_name)
    log_model_class = get_log_class(model_name)
    readonly = get_readonly_fields(log_model_class)

    class ModelAdmin(ReallyDeleteAdmin):

        model = model_class
        list_display = ('name', 'price', )

    class ModelLogAdmin(ReallyDeleteAdmin):

        list_display = ('finance_object', 'price', 'delta_price', 'delta_margin', 'created_time')
        list_filter = ('finance_object__name',)
        model = log_model_class
        readonly_fields = readonly

        def has_add_permission(self, *args, **kwargs):
            return False

    admin.site.register(model_class, ModelAdmin)
    if model_class.need_log:
        admin.site.register(log_model_class, ModelLogAdmin)

for model_name in finance_categories:
    register(model_name)

class ExtraDataAdmin(admin.ModelAdmin):

    model = ExtraData
    list_display = ('display_name', 'value')

    def has_delete_permission(self, request, obj = None):
        if obj is None or not obj.removeable:
            return False

        return obj.key not in ('index', 'year')

class PlayerDataLogAdmin(admin.ModelAdmin):

    model = PlayerDataLog
    readonly_fields = get_readonly_fields(model)
    list_display = ('user', 'stock', 'output_value', 'status')

    def has_add_permission(self, *args, **kwargs):
        return False

class PlayerDataTotalLogAdmin(admin.ModelAdmin):

    model = PlayerDataTotalLog
    readonly_fields = get_readonly_fields(model)
    list_display = ('user', 'finance_year', 'stock', 'output_value')

    def has_add_permission(self, *args, **kwargs):
        return False

admin.site.register(ExtraData, ExtraDataAdmin)
admin.site.register(PlayerDataLog, PlayerDataLogAdmin)
admin.site.register(PlayerDataTotalLog, PlayerDataTotalLogAdmin)