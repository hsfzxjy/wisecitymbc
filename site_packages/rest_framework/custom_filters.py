from django_filters import FilterSet, NumberFilter

__all__ = ['get_timeline_filter', 'is_timeline_filter']

class TimelineFilter(object):
    pass

def is_timeline_filter(obj):
    return issubclass(obj.__class__, TimelineFilter)

def get_timeline_filter(model_class, base_filter_class = FilterSet): 

    if not base_filter_class:
        base_filter_class = FilterSet

    class _TimelineFilter(base_filter_class, TimelineFilter):

        sinceid = NumberFilter(name = 'pk', lookup_type = 'gt')
        beforeid = NumberFilter(name = 'pk', lookup_type = 'lt')

        class Meta(getattr(base_filter_class,'Meta',object)):
            model = model_class

    return _TimelineFilter