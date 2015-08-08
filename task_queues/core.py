from app_cache import AppCache
from django.conf.urls import patterns

class TaskQueueCache(AppCache):

	module_name = 'task_queue_urls'
	object_name = 'urlpatterns'
	default_object = patterns('')

cache = TaskQueueCache()