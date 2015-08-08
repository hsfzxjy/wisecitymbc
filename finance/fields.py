from django.db import models
from functools import partial

DecimalField = partial(
        models.DecimalField,
        max_digits = 60,
        decimal_places = 2
)
