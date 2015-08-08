from django.core.cache.backends.base import BaseCache, DEFAULT_TIMEOUT

from time import time

from saekv.base import kv

PERSISTENT_TIMEOUT = 0

class KVCache(BaseCache):

    def __init__(self, location, params):
        return super(KVCache, self).__init__(params)

    def get_backend_timeout(self, timeout=DEFAULT_TIMEOUT):
        if timeout == PERSISTENT_TIMEOUT:
            return timeout

        return super(KVCache, self).get_backend_timeout(timeout)

    def make_key(self, *args, **kwargs):
        key = super(KVCache, self).make_key(*args, **kwargs)
        return key.encode('utf8')

    def _is_expired(self, timestamp):
        if not isinstance(timestamp, (float, int, long)):
            return True

        if timestamp == PERSISTENT_TIMEOUT:
            return False

        return timestamp < time()

    def _delete_if_expired(self, key, timestamp, obj):
        if self._is_expired(timestamp):
            if obj is not None:
                self.delete(key)
            return None
        else:
            return obj

    def set(self, key, value, timeout = DEFAULT_TIMEOUT, version = None):
        key = self.make_key(key, version = version)
        kv.set(key, self.get_backend_timeout(timeout), value)

    def delete(self, key, version = None):
        key = self.make_key(key, version = version)
        kv.delete(key)

    def add(self, key, value, timeout = DEFAULT_TIMEOUT, version = None):
        key = self.make_key(key, version = version)
        old_object = self.get(key, version = version)
        if old_object is not None:
            return False

        return kv.add(key, self.get_backend_timeout(timeout), value)

    def get(self, key, default=None, version = None):
        key = self.make_key(key, version = version)
        timestamp, obj = kv.get(key)
        obj = self._delete_if_expired(key, timestamp, obj)
        
        if obj is None:
            return default

        return obj