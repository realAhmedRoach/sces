from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UUIDField
import uuid
from sces import commodity


class ExchangeUser(AbstractUser):
    party = models.ForeignKey(verbose_name='Party', to='Party', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.username


class Party(models.Model):
    uid = UUIDField(verbose_name='UID', primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    symbol = models.CharField(verbose_name='Symbol', max_length=4, unique=True)
    name = models.CharField(verbose_name='Name', max_length=120, unique=True)

    def __str__(self):
        return '%s - %s' % (self.symbol, self.name)

    class Meta:
        verbose_name_plural = 'Parties'


class BidAskManager(models.Manager):
    def get_queryset(self):
        return super(BidAskManager, self).get_queryset().filter(filled=False)

    def bid(self, cmdty):
        return self.get_queryset().filter(commodity=cmdty, side='BUY').order_by('price', '-order_time').first()

    def ask(self, cmdty):
        return self.get_queryset().filter(commodity=cmdty, side='SELL').order_by('-price', '-order_time').first()


class Order(models.Model):
    TRADE_SIDES = (('BUY', 'BUY'), ('SELL', 'SELL'))
    ORDER_TYPES = (('MRKT', 'Market'), ('LMT', 'Limit'))

    uid = UUIDField(verbose_name='UID', primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    party = models.ForeignKey(verbose_name='Party', to=Party, on_delete=models.SET_NULL, null=True)
    order_time = models.DateTimeField(verbose_name='Order Time', auto_now_add=True)
    commodity = models.CharField(verbose_name='Commodity', max_length=2, choices=commodity.get_commodity_choices())
    quantity = models.PositiveIntegerField(verbose_name='Quantity')
    price = models.DecimalField(verbose_name='Price', max_digits=7, decimal_places=4)
    side = models.CharField(verbose_name='Trade Side', max_length=4, choices=TRADE_SIDES)
    order_type = models.CharField(verbose_name='Order Type', max_length=4, choices=ORDER_TYPES,
                                  default=ORDER_TYPES[0][0])
    filled = models.BooleanField(verbose_name='Filled?', default=False)

    objects = models.Manager()
    bidask = BidAskManager()

    def __str__(self):
        symbol = self.party.symbol if self.party else 'NONE'
        return '%s %s@%s (%s)' % (symbol, self.side, self.commodity, self.order_time)

    class Meta:
        get_latest_by = 'order_time'
        ordering = ['filled', '-order_time']