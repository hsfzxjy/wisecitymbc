from django.test import TestCase

from .models import Stock, StockLog, ExtraData

class StockTestCase(TestCase):
    def setUp(self):
        Stock.objects.create(name = '34', price = '34')
        ExtraData.objects.create(key = '34')