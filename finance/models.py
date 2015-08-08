#encoding=utf8
from decimal import Decimal
from django.db import models
from .fields import DecimalField
from common.utils import getattrex, getattrlazy
from django.utils.datastructures import SortedDict
from django.core.validators import MaxValueValidator, MinValueValidator

import warnings

warnings.filterwarnings('ignore', 'Data truncated .*')

VERBOSE = u'所属对象'

get_log_class = lambda model_name: globals()[model_name.title()+'Log']
get_finance_class = lambda model_name: globals()[model_name.title()]

class UndoableMixin(object):

    target_field_name = 'finance_object'

    def _get_next_log(self):
        if hasattr(self, '_next_log'):
            return self._next_log

        try:
            self._next_log = self.__class__.objects.filter(**{
                self.target_field_name: getattr(self, self.target_field_name),
                'created_time__gt': self.created_time
            })[0]
        except IndexError:
            self._next_log = None

        return self._next_log

    @staticmethod
    def _inc_object_field_value(obj, field_name, delta):
        """
        For a given object, add its `field_name` field by value delta.
        Returns the new value.
        """
        old_value = getattr(obj, field_name)
        new_value = old_value + delta
        setattr(obj, field_name, new_value)
        return new_value

    def restore_field_value(self, field_name, delta_margin = False, target_value_field_name = '', delta = None):
        """
        When myself is going to be deleted, call the method to alter the next log automatically.
        """

        delta_field_name = 'delta_{0}'.format(field_name)
        next_log = self._get_next_log()

        if delta is None:
            delta = -getattr(self, delta_field_name)

        last_value = getattr(self, field_name) - getattr(self, delta_field_name)
        self._inc_object_field_value(self, delta_field_name, delta)
        self._inc_object_field_value(self, field_name, delta)
        # TODO : MARGIN

        if not next_log:
            target = getattr(self, self.target_field_name)
            print target_value_field_name
            target_value_field_name = target_value_field_name or field_name
            self._inc_object_field_value(target, target_value_field_name, delta)
        else:            
            next_log_delta = getattr(next_log, delta_field_name)
            delta = next_log_delta - delta

            if delta_margin:
                next_log.delta_margin *= delta / next_log_delta if next_log_delta else 0

            setattr(next_log, delta_field_name, delta) 

        return next_log

    def dec_value(self, field_name, delta_value):
        pass

class SecurityBase(models.Model):

    name = models.CharField(u'名称', max_length=50)
    price = DecimalField(u'价格')

    need_log = True

    col_width = 6

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name

    def delete(self, *args, **kwargs):
        for log in self.get_log_class().objects.filter(finance_object = self):
            log.delete()

        return super(SecurityBase, self).delete(*args, **kwargs)

    @classmethod 
    def meta(cls):
        return cls._meta

    @classmethod
    def register_field(cls, 
            field_list, 
            field_name, 
            verbose_name = '', 
            front = False, 
            **kwargs
        ):
        if not verbose_name:
            verbose_name = cls._meta.get_field_by_name(field_name)[0].verbose_name

        field_descriptor = SortedDict([
            ('field_name', field_name),
            ('name', verbose_name),
            ('col_width', kwargs.get('col_width', cls.col_width)),
        ] + kwargs.items())

        if front:
            field_list.insert(0, field_descriptor)
        else:
            field_list.append(field_descriptor)

        return field_descriptor

    @classmethod
    def unregister_field(cls, field_list, field_name):
        matched_fields = filter(lambda field: field['field_name'] == field_name, field_list)
        map(lambda field: field_list.remove(field), matched_fields)

    @classmethod
    def get_display_fields(cls):
        fields = []
        cls.register_field(fields, 'price', status_css = True)
        cls.register_field(fields, 'last_log.delta_margin', u'涨跌幅', with_percentage = True, status_css = True)

        cls._get_display_fields(fields)

        return fields

    @classmethod
    def _get_display_fields(cls, field_list):
        return

    @property 
    def url(self):
        return "/finance/{0}/{1}/".format(
            self.__class__.__name__.lower(),
            self.pk
        )

    @property 
    def last_log(self):
        cls = self.get_log_class()

        try:
            return cls.objects.filter(finance_object = self)[0]
        except (cls.DoesNotExist, IndexError):
            return None

    @property 
    def display_data(self):
        if not hasattr(self, '_display_data'):
            field_names = self.get_display_fields()
            self._display_data = []

            for field_dict in field_names:
                obj = {}
                obj.update(field_dict)
                field_name = obj['field_name']
                obj['value'] = getattrlazy(self, field_name, None)
                self._display_data.append(obj)

        return self._display_data

    @classmethod
    def get_log_class(cls):
        return globals()[cls.__name__+'Log']

    def create_log(self, create):
        return self.get_log_class().create_log(self)

    def save(self, create_log = True, *args, **kwargs):
        create = not (self.pk)
        super(SecurityBase, self).save(*args, **kwargs)
        if create_log:
            self.create_log(create)


class SecurityLogBase(models.Model, UndoableMixin):

    price = DecimalField(u'新价格')
    delta_price = DecimalField(u'变更量')
    delta_margin = DecimalField(u'涨跌幅')
    created_time = models.DateTimeField(u'变更时间', auto_now_add=True)

    class Meta:
        abstract = True 
        ordering = ('-created_time',)

    @classmethod
    def _do_get_extra_chart_fields(cls, fields):
        pass

    @classmethod
    def _register_extra_chart_field(cls, fields, field_name, type = 'line'):
        fields.append((field_name, cls._meta.get_field_by_name(field_name)[0].verbose_name, type))

    @classmethod
    def get_extra_chart_fields(cls):
        fields = []
        cls._do_get_extra_chart_fields(fields)
        return fields

    @classmethod
    def get_last_log(cls, finance_object):
        try:
            return cls.objects.filter(finance_object = finance_object)[0]
        except IndexError:
            return None

    def pre_delete(self, next_log):
        pass

    def delete(self, ignore = False, *args, **kwargs):
        if not ignore:
            next_log = self.restore_field_value('price', True)

            self.pre_delete(next_log)
            if next_log:
                next_log.save()
            else:
                self.finance_object.save(create_log = False)

        super(SecurityLogBase, self).delete(*args, **kwargs)

    @classmethod
    def process_log(cls, finance_instance, log, last_log):
        pass

    @classmethod
    def create_log(cls, finance_instance):
        last_log = cls.get_last_log(finance_instance)

        if last_log and finance_instance.price == last_log.price:
            return

        last_price = last_log.price if last_log else 0
        delta_price = finance_instance.price - last_price
        delta_margin = delta_price * 100 / last_price if last_price else 0
        log = cls(
            price = finance_instance.price, 
            delta_price = delta_price,
            delta_margin =  delta_margin,
            finance_object = finance_instance
        )

        cls.process_log(finance_instance, log, last_log)

        log.save()

        return log

    @property 
    def status(self):
        if self.delta_price > 0:
            return 'up'
        elif self.delta_price == 0:
            return ''
        else:
            return 'down'

    def __unicode__(self):
        return u'{0} 在 {1} 的变更：{2}'.format(
            self.finance_object.name, 
            self.created_time, 
            self.delta_price
        )

class Stock(SecurityBase):

    volume = DecimalField(u'成交量')
    description = models.TextField(u'股票信息', default = u'未填写股票信息')
    weight = DecimalField(u'权值', default = 5)

    @classmethod
    def get_total_weight(cls):
        from django.db.models import Sum
        total_weight = Stock.objects.all().aggregate(result = Sum('weight'))['result']
        return total_weight

    def create_log(self, create):
        stock_log = super(Stock, self).create_log(create)

        if not create:
            if not stock_log:
                return

            stock_log.index_log = DataLog.create_index_log(stock_log)
            stock_log.save()

        return stock_log

    @classmethod
    def _get_display_fields(cls, field_list):
        cls.register_field(field_list, 'volume')
        cls.register_field(field_list, 'description', front = True, 
            col_width = 12,
            extra_css = 'stock-description'
        )

    class Meta:
        verbose_name = verbose_name_plural = u'股票'

class StockLog(SecurityLogBase):

    finance_object = models.ForeignKey(Stock, related_name='logs', verbose_name = VERBOSE)
    index_log      = models.ForeignKey('DataLog', related_name='stock_logs', null = True)
    volume         = DecimalField(u'成交量') 
    delta_volume   = DecimalField(u'成交量变更')
    delta_index    = DecimalField()
    
    @classmethod
    def _do_get_extra_chart_fields(cls, fields):
        cls._register_extra_chart_field(fields, 'volume', 'column')

    @classmethod
    def process_log(cls, finance_instance, log, last_log):
        last_volume = last_log.volume if last_log else 0
        delta_volume = finance_instance.volume - last_volume
        log.delta_volume = delta_volume
        log.volume = finance_instance.volume
        log.delta_index = 1+finance_instance.weight * (log.delta_margin / 100) / Stock.get_total_weight()

    def pre_delete(self, next_log):
        self.restore_field_value('volume')
        DataLog.do_remove_stock_log(self)

    def delete(self, *args, **kwargs):
        next_log = self._get_next_log()
        if next_log:
            try:
                #next_log.delta_index *= (1 + self.delta_price / next_log.delta_price)
                next_log.delta_index += self.delta_index
            except ZeroDivisionError:
                pass 

        super(StockLog, self).delete(*args, **kwargs)

    class Meta(SecurityLogBase.Meta):
        verbose_name=verbose_name_plural=u'股票变更记录'

class Future(SecurityBase):

    class Meta:
        verbose_name = verbose_name_plural = u'期货'

class FutureLog(SecurityLogBase):

    finance_object = models.ForeignKey(Future, related_name='logs', verbose_name = VERBOSE)

    class Meta(SecurityLogBase.Meta):
        verbose_name=verbose_name_plural=u'期货变更记录'

class Goods(SecurityBase):

    class Meta:
        verbose_name = verbose_name_plural = u'大宗交易'

class GoodsLog(SecurityLogBase):

    finance_object = models.ForeignKey(Goods, related_name='logs', verbose_name = VERBOSE)

    class Meta(SecurityLogBase.Meta):
        verbose_name=verbose_name_plural=u'大宗交易变更记录'

class Bond(SecurityBase):

    need_log = False
    col_width = 4

    rating = models.CharField(u'评级', max_length=25, choices = map(lambda x: [x]*2, ['A', 'B', 'C', 'D', 'E']))
    interest_rate = DecimalField(u'利率', validators=[MaxValueValidator(100), MinValueValidator(0)])

    class Meta:
        verbose_name = verbose_name_plural = u'债券'

    @classmethod
    def _get_display_fields(cls, field_list):
        cls.register_field(field_list, 'rating')
        cls.register_field(field_list, 'interest_rate', with_percentage = True)

class BondLog(SecurityLogBase):

    finance_object = models.ForeignKey(Bond, related_name='logs', verbose_name = VERBOSE)

    class Meta(SecurityLogBase.Meta):
        verbose_name=verbose_name_plural=u'债券变更记录'

from decimal import Decimal

class ExtraData(models.Model):

    key = models.CharField(u'标识符', unique = True, max_length=255, db_index = True, )
    display_name = models.CharField(u'显示名称', max_length=255, unique=True)
    value = models.TextField(u'值')
    removeable = models.BooleanField(default = True)
    display_on_home_page = models.BooleanField(u'在网页上显示', default = True)

    class Meta:
        verbose_name = verbose_name_plural = u'其他数据'

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.display_name

        super(ExtraData, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.display_name

    @property 
    def decimal_value(self):
        return Decimal(self.value)

    @decimal_value.setter
    def decimal_value(self, value):
        self.value = value

class DataLog(SecurityLogBase, UndoableMixin):

    data = models.ForeignKey('ExtraData', related_name='logs', verbose_name = u'所属数据条目')

    class Meta(SecurityLogBase.Meta):
        verbose_name = verbose_name_plural = u'其他数据变更记录'

    target_field_name = 'data'

    @classmethod
    def do_remove_stock_log(cls, stock_log):
        delta = -stock_log.delta_index
        related_log = stock_log.index_log
        if not related_log:
            return

        next_log = related_log.restore_field_value('price', True, 'decimal_value', delta)

        if next_log:
            next_log.save()
        else:
            related_log.data.save()

        if not related_log.delta_price:
            related_log.delete(ignore = True)
        else:
            related_log.save()
        # delta = stock_log.delta_index

        # first_log = stock_log.index_log
        # if not first_log:
        #     return

        # old_value = first_log.price - first_log.delta_price 
        # first_log.delta_price -= delta
        # first_log.delta_margin = first_log.delta_price * 100 / old_value if old_value else 0
        # first_log.price = old_value

        # try:
        #     index_obj = ExtraData.objects.get(key = 'index')
        #     index_obj.decimal_value -= delta
        #     index_obj.save()
        # except ExtraData.DoesNotExist:
        #     return

        # from django.db.models import F
        # logs = cls.objects \
        #     .filter(data = index_obj, created_time__gt = first_log.created_time)
        # logs.update(
        #         price = F('price') - delta,
        #         delta_margin = F('delta_price') * Decimal(100) / (F('price')-F('delta_price'))
        #     )
        # if not first_log.delta_price:
        #     first_log.delete(ignore = True)
        # else:
        #     first_log.save()


    @classmethod
    def create_index_log(cls, stock_log):
        try:
            index_obj = ExtraData.objects.get(key = 'index')
        except ExtraData.DoesNotExist:
            return

        delta_margin = stock_log.delta_index
        print delta_margin
        current_index = index_obj.decimal_value
        new_index = current_index * delta_margin
        delta_price = new_index - current_index
        stock_log.delta_index = delta_price

        log = cls.objects.create(
            data = index_obj,
            price = new_index,
            delta_price = delta_price,
            delta_margin = delta_price * 100 / current_index if current_index else 0
        )

        index_obj.decimal_value = new_index
        index_obj.save()

        return log

class PlayerDataBase(models.Model):

    user = models.ForeignKey('accounts.User', related_name='%(class)s_player_data_logs', verbose_name = u'选手')
    stock = DecimalField(verbose_name = u'股票涨幅')
    output_value = DecimalField(verbose_name = u'产值涨幅')
    created_time = models.DateTimeField(u'修改时间', auto_now_add=True, db_index=True)

    common_fields = ('stock', 'output_value')

    class Meta:
        ordering = ('-created_time',)
        abstract = True

    def __unicode__(self):
        return u'记录{0}'.format(self.id)

class PlayerDataLog(PlayerDataBase):

    status = models.ForeignKey('articles.Status', verbose_name = u'所属文章')

    @classmethod
    def summary(cls, year):
        from django.db.models import Sum
        kwargs = {
            name: Sum(name) for name in cls.common_fields
        }
        logs = cls.objects.values('user_id').annotate(**kwargs)

        for log in logs:
            log['finance_year'] = year

        PlayerDataTotalLog.objects.bulk_create(map(
            lambda x: PlayerDataTotalLog(**x),
            logs
        ))

        cls.objects.all().delete()
        
    class Meta:
        verbose_name = verbose_name_plural = u'选手数据'


class PlayerDataTotalLog(PlayerDataBase):

    finance_year = models.PositiveIntegerField(u'财年')
    
    class Meta:
        verbose_name = verbose_name_plural = u'选手数据统计'

import signal_receivers
