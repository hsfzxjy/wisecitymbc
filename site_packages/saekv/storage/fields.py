from saekv.base import kv
from collections import Iterable
from copy import deepcopy
from time import time

from .exceptions import AwaitTimeout
from .decorators import do_if_unlocked

__all__ = ['KVModel']

KEY_PREFIX = 'saekv.storage'

def is_a_collection(obj):
    return isinstance(obj, Iterable) and not isinstance(obj, basestring)

def get_iterator(obj):
    if not is_a_collection(obj):
        return
    
    return obj.iteritems() if isinstance(obj, dict) else enumerate(obj)

class KVModel(object):

    UNSAVED = 'unsaved'
    SAVED = 'saved'

    def __init__(self, parent = None, key = None, value = None):
        self.__value_is_a_collection = False
        self.__locked = False
        self.__timestamp = None
        self.__value = deepcopy(value)
        self.__key = None
        self.__state = self.SAVED
        if key is not None:
            self.__key = self.make_key(key)

        self.__parent = parent
        
        if self.__key:
            if not self.__value:
                self.update()
            else:
                self.__state = self.UNSAVED
        else:
            if not self.__parent:
                raise Exception('Neither `key` nor `parent` is defined.')

            self._update_info()

        self._process_value()

    def __iter__(self):
        if not self.__value_is_a_collection:
            raise NotImplementedError

        return get_iterator(self.__value)

    def __getattr__(self, key):
        try:
            if key.startswith('_'):
                raise KeyError

            return self._getattr(key)
        except (KeyError, TypeError):
            return object.__getattribute__(self, key)

    def __setattr__(self, key, value):
        try:
            if not key.startswith('_'):
                self._setattr(key, value)
                return
        except (KeyError, TypeError):
            pass
        finally:
            object.__setattr__(self, key, value)

    def __delattr__(self, key):
        self._delattr(key)

    def __setitem__(self, key, value):
        self._setattr(key, value)
        
    def __getitem__(self, key):
        return self._getattr(key)

    def __delitem__(self, key):
        self._delattr(key)

    def _delattr(self, key):
        if not self.__value_is_a_collection:
            raise KeyError(key)

        del self.__value[key]

    def _extract_info(self, info):
        if info is None:
            return False, None 

        return info['locked'], info['timestamp']

    def _process_info(self, info):
        self.__locked, self.__timestamp = self._extract_info(info)

    def _get_info(self):
        return kv.get(self.__key)[0]

    def _update_info(self):
        if self.__state == self.UNSAVED:
            return

        if self.parent:
            self.__locked = self.parent.locked
            self.__timestamp = self.parent.timestamp
        else:
            info = self._get_info()
            self._process_info(info)

    @classmethod
    def _get_default(self):
        return {}

    @classmethod
    def _get_field_class(cls, key):
        return KVModel

    def _setattr(self, key, value):
        if not self.__value_is_a_collection:
            raise KeyError(key)

        if not isinstance(value, KVModel):
            value = self._get_field_class(key)(value = value, parent = self)

        self.__value[key] = value

    def _getattr(self, key):
        if not self.__value_is_a_collection:
            raise KeyError(key)

        result = self.__value[key]
        if not result.value_is_a_collection:
            result = result.__value

        return result        

    def _to_python(self):
        result = self.__value

        if self.__value_is_a_collection:
            result = self.__value.__class__()
            for key, value in get_iterator(self.__value):
                result[key] = value._to_python()

        return result

    def _process_value(self):
        if self.__value is None:
            self.__value = self._get_default()

        self.__value_is_a_collection = is_a_collection(self.__value)

        if isinstance(self.__value, KVModel):
            self.__value = self.__value._to_python()
        elif self.__value_is_a_collection:
            if isinstance(self.__value, Iterable) and not isinstance(self.__value, dict):
                self.__value = list(self.__value)

            for key, value in get_iterator(self.__value):
                self._setattr(key, value)

    @property 
    def state(self):
        return self.__state

    @property 
    def timestamp(self):
        return self.__timestamp

    @property 
    def parent(self):
        return self.__parent

    @property 
    def value_is_a_collection(self):
        return self.__value_is_a_collection

    @property
    def value(self):
        if self.__value_is_a_collection:
            return self._to_python()

        return self.__value

    @value.setter
    def value(self, new_value):
        self.__value = new_value
        self._process_value()

    @property 
    def locked(self):
        return self.__locked

    def make_key(self, key):
        return (KEY_PREFIX+self.__class__.__name__+str(key)).encode('utf8')

    def get_lock_state(self):
        return self._extract_info(self._get_info())[0]

    def lock(self):
        if self.locked:
            return False

        if self.get_lock_state():
            return False

        self.__locked = True
        self.save()

        return True

    def await(self, timeout = -1):
        if self.locked:
            return False

        end_time = time() + timeout
        waited = False
        while True:
            if self.get_lock_state():
                waited = True
                if timeout > 0 and time() > end_time:
                    raise AwaitTimeout()
            else:
                break

        return waited

    def unlock(self):
        if not self.locked:
            return False

        self.__locked = False
        self.save()

        return True   

    def update(self):
        if not self.__key:
            result = self.parent.update()
            self._update_info()

        info, self.__value = kv.get(self.__key, None)
        self.__state = self.UNSAVED if info is None else self.SAVED
        self.__timestamp = self._extract_info(info)[1]
        self._process_value()

        return True

    def save(self):
        if not self.__key:
            return self.parent.save()

        self.__timestamp = time()
        kv.set(self.__key, {
            'timestamp': self.__timestamp,
            'locked': self.__locked
        }, self._to_python())
        kv.__state = self.SAVED
        
        return True

    def swap(self, field1, field2):
        if not self.__value_is_a_collection:
            return

        self.__value[field1], self.__value[field2] = self.__value[field2], self.__value[field1]

class KVModel_(KVModel):

    @classmethod
    def get_default(cls):
        return None

    @classmethod
    def get(cls, key, default = None):
        default = default or cls.get_default()
        _, result = kv.get(make_key(key), default)

        if result is not None:
            return cls(value = result, key = key)

        return result

    @classmethod
    def get_or_create(cls, key, default = None, save = True):
        result = cls.get(key, default = default)

        if result is None:
            result = cls.create(key, {}, save)

        return result

    @classmethod
    def create(cls, key, value, save = False):
        if isinstance(value, KVModel):
            obj = value
            obj.set_key(key)
        else:
            obj = cls(key = key, value = value)
        
        if save:
            obj.save()

        return obj