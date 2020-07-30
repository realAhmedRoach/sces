from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import F
import uuid

from sces.commodity import get_commodity_choices, get_valid_contracts


class ExchangeUser(AbstractUser):
    party = models.ForeignKey(verbose_name='Party', to='Party', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.username


class Party(models.Model):
    uid = models.UUIDField(verbose_name='UID', primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    symbol = models.CharField(verbose_name='Symbol', max_length=4, unique=True)
    name = models.CharField(verbose_name='Name', max_length=120, unique=True)

    def __str__(self):
        return '%s - %s' % (self.symbol, self.name)

    class Meta:
        verbose_name_plural = 'Parties'


class WarehouseReceipt(models.Model):
    uid = models.UUIDField(verbose_name='UID', primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    created_time = models.DateTimeField(verbose_name='Created Time', auto_now_add=True)
    commodity = models.CharField(verbose_name='Commodity', max_length=2, choices=get_commodity_choices())
    quantity = models.PositiveIntegerField(verbose_name='Quantity')
    party = models.ForeignKey(verbose_name='Party', to='Party', on_delete=models.CASCADE)

    def __str__(self):
        return '<%s> %s%s @%s' % (self.party, self.quantity, self.commodity, self.created_time)


class BidAskManager(models.Manager):
    def get_queryset(self):
        return super(BidAskManager, self).get_queryset().filter(quantity_filled__lt=F('quantity')).annotate(
            quantity_unfilled=F('quantity') - F('quantity_filled'))

    def bid(self, contract_code):
        return self.get_queryset().filter(commodity=contract_code[:2], contract=contract_code[-3:], side='BUY')\
            .order_by('price', '-order_time').first()

    def ask(self, contract_code):
        return self.get_queryset().filter(commodity=contract_code[:2], contract=contract_code[-3:], side='SELL')\
            .order_by('-price', '-order_time').first()


class Order(models.Model):
    TRADE_SIDES = (('BUY', 'BUY'), ('SELL', 'SELL'))
    ORDER_TYPES = (('MRKT', 'Market'), ('LMT', 'Limit'))

    uid = models.UUIDField(verbose_name='UID', primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    party = models.ForeignKey(verbose_name='Party', to=Party, on_delete=models.CASCADE, null=True)
    order_time = models.DateTimeField(verbose_name='Order Time', auto_now_add=True)
    commodity = models.CharField(verbose_name='Commodity', max_length=2, choices=get_commodity_choices())
    quantity = models.PositiveIntegerField(verbose_name='Quantity')
    contract = models.CharField(verbose_name='Contract', max_length=4, choices=get_valid_contracts())
    price = models.DecimalField(verbose_name='Price', max_digits=7, decimal_places=4)
    side = models.CharField(verbose_name='Trade Side', max_length=4, choices=TRADE_SIDES)
    order_type = models.CharField(verbose_name='Order Type', max_length=4, choices=ORDER_TYPES,
                                  default=ORDER_TYPES[0][0])
    quantity_filled = models.PositiveIntegerField(verbose_name='Quantity Filled', default=0)

    objects = models.Manager()
    bidask = BidAskManager()

    def __str__(self):
        symbol = self.party.symbol if self.party else 'NONE'
        return '<%s> %s %s%s (%s)' % (symbol, self.side, self.commodity, self.contract, self.order_time)

    class Meta:
        get_latest_by = 'order_time'
        ordering = ['-order_time']
