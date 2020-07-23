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
    uid = UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(verbose_name='Name', max_length=120, unique=True)
    symbol = models.CharField(verbose_name='Symbol', max_length=4, unique=True)

    class Meta:
        verbose_name_plural = 'Parties'


class Order(models.Model):
    TRADE_SIDES = (('BUY', 'BUY'), ('SELL', 'SELL'))

    uid = UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    party = models.ForeignKey(verbose_name='Party', to=Party, on_delete=models.SET_NULL, null=True)
    order_time = models.DateTimeField(verbose_name='Order Time', auto_now_add=True)
    commodity = models.CharField(verbose_name='Commodity', max_length=2, choices=commodity.get_commodity_choices())
    quantity = models.PositiveIntegerField(verbose_name='Quantity')
    price = models.DecimalField(verbose_name='Price', max_digits=7, decimal_places=4)
    side = models.CharField(verbose_name='Trade Side', max_length=4, choices=TRADE_SIDES)
    filled = models.BooleanField(verbose_name='Filled?', default=False)
