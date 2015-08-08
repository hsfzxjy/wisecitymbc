from .exceptions import AwaitTimeout
from functools import wraps

def do_if_unlocked(timeout = 0, update = True, lock = True, do = False):

    def inner(func):

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            locked = self.await(timeout = timeout)

            try:
                if lock:
                    self.lock()

                if locked:
                    if update:
                        self.update()

                    if not do:
                        return

                return func(self, *args, **kwargs)
            finally:
                if lock:
                    self.unlock()

        return wrapper

    return inner