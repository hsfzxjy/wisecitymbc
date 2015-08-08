from django.dispatch import Signal

finance_year_changed = Signal(providing_args = ['post_year', 'current_year'])