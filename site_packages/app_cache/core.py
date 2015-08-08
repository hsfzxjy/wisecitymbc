from django.utils.importlib import import_module
from django.utils.module_loading import module_has_submodule
from django.apps import apps

class AppCache(object):

    module_name = ''
    object_name = ''
    default_object = ''

    def __init__(self, *args, **kwargs):
        self.__module_name = '.%s' % self.module_name

    def get_objects(self):
        for mod in self.get_modules():
            yield getattr(mod, self.object_name, self.default_object)

    def get_modules(self):

        for app_config in apps.get_app_configs():
            if not module_has_submodule(app_config.module, self.module_name):
                continue

            yield import_module(self.__module_name, app_config.name)