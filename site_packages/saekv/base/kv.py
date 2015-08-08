from sae.kvdb import KVClient

kvclient = KVClient(debug = True)

def wrap_object(extra, obj):
    return {
        'extra': extra,
        'obj': obj
    }

def extract_object(obj, default = None):
    if obj is None:
        return None, default

    return obj.get('extra', None), obj.get('obj', default)

def set(key, config, obj):
    return kvclient.set(key, wrap_object(config, obj))

def get(key, default = None):
    return extract_object(kvclient.get(key), default)

def add(key, config, obj):
    return kvclient.add(key, wrap_object(config, obj))

def delete(key):
    return kvclient.delete(key)