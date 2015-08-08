from app_cache import AppCache

class APICache(AppCache):

    default_object = ()
    object_name = 'routers'
    module_name = 'routers'

    def get_routers(self):
        results = []
        for obj in self.get_objects():
            results.extend(obj)
        return results

cache = APICache()