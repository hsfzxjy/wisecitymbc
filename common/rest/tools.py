from rest_framework.renderers import JSONRenderer
from rest_framework.serializers import Serializer

def render_to_json(data):
    if isinstance(data, Serializer):
        data = data.data
        
    return JSONRenderer().render(data)