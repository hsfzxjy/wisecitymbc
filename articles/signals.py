from django.dispatch import Signal

status_posted = Signal(providing_args = ['data'])