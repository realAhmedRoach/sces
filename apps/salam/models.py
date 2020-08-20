import uuid

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F
from django.utils.translation import gettext_lazy as _

from apps.salam.validators import validate_contract_code, validate_is_warehouse
from sces.commodity import get_commodity_choices, get_valid_contracts


class ExchangeUser(AbstractUser):
    """Custom user model with foreignkey to firm"""
    firm = models.ForeignKey(verbose_name='Firm', to='Firm', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.username


class Firm(models.Model):
    """Firm model, represents entity that can make orders and own commodities"""
    FIRM_TYPES = (('WRHS', 'Warehouse'), ('PROD', 'Producer'), ('CONS', 'Consumer'), ('TRAD', 'Trader'))

    uid = models.UUIDField(verbose_name='UID', primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    symbol = models.CharField(verbose_name='Symbol', max_length=4, unique=True)
    name = models.CharField(verbose_name='Name', max_length=120, unique=True)
    type = models.CharField(verbose_name='Type', max_length=4, choices=FIRM_TYPES)

    def __str__(self):
        return f'<{self.symbol}> {self.name}'


class WarehouseReceiptManager(models.Manager):
    """Custom manager for WarehouseReceipt; has custom filter based on firm"""
    def get_filtered_queryset(self, firm: Firm):
        return self.get_queryset().filter(models.Q(firm=firm) | models.Q(warehouse=firm))


class WarehouseReceipt(models.Model):
    """WarehouseReceipt model, represents ownership of a commodity"""
    uid = models.UUIDField(verbose_name='UID', primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    created_time = models.DateTimeField(verbose_name='Created Time', auto_now_add=True)
    commodity = models.CharField(verbose_name='Commodity', max_length=2, choices=get_commodity_choices())
    quantity = models.PositiveIntegerField(verbose_name='Quantity')
    firm = models.ForeignKey(verbose_name='Firm', to='Firm', related_name='firm', on_delete=models.CASCADE, null=True,
                             blank=True)
    warehouse = models.ForeignKey(verbose_name='Warehouse', to='Firm', related_name='warehouse',
                                  on_delete=models.CASCADE, validators=[validate_is_warehouse])

    receipts = WarehouseReceiptManager()

    def clean(self):
        if self.firm == self.warehouse:
            raise ValidationError(_('The warehouse cannot own a commodity in its own location'),
                                  code='firm_ne_warehouse')

    def __str__(self):
        return f'<{self.firm}> {self.quantity} {self.commodity} ({self.created_time})'

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(firm=F('warehouse')), name='firm_ne_warehouse')
        ]


class BidAskManager(models.Manager):
    """Gets bids and asks from orders"""
    def get_queryset(self):
        return super(BidAskManager, self).get_queryset().filter(quantity_filled__lt=F('quantity'))

    def bids(self, contract_code):
        return self.get_queryset().filter(commodity=contract_code[:2], contract=contract_code[-3:], side='BUY',
                                          order_type='LMT')

    def asks(self, contract_code):
        return self.get_queryset().filter(commodity=contract_code[:2], contract=contract_code[-3:], side='SELL',
                                          order_type='LMT')

    def best_bid(self, contract_code, caller=None):
        if caller:
            self.bids(contract_code).exclude(firm=caller.firm).order_by('price', 'order_time').first()
        return self.bids(contract_code).order_by('-price', 'order_time').first()

    def best_ask(self, contract_code, caller=None):
        if caller:
            self.asks(contract_code).exclude(firm=caller.firm).order_by('-price', 'order_time').first()
        return self.asks(contract_code).order_by('price', 'order_time').first()


class Order(models.Model):
    """
    Order, represents intent to buy or sell commmodity in market at specified contract date, with immediate payment
    """
    TRADE_SIDES = (('BUY', 'BUY'), ('SELL', 'SELL'))
    ORDER_TYPES = (('MRKT', 'Market'), ('LMT', 'Limit'))

    uid = models.UUIDField(verbose_name='UID', primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    firm = models.ForeignKey(verbose_name='Firm', to='Firm', on_delete=models.CASCADE, null=True)
    order_time = models.DateTimeField(verbose_name='Order Time', auto_now_add=True)
    commodity = models.CharField(verbose_name='Commodity', max_length=2, choices=get_commodity_choices())
    contract = models.CharField(verbose_name='Contract', max_length=4, choices=get_valid_contracts(),
                                validators=[validate_contract_code])
    price = models.DecimalField(verbose_name='Price', max_digits=8, decimal_places=3)
    quantity = models.PositiveIntegerField(verbose_name='Quantity')
    side = models.CharField(verbose_name='Trade Side', max_length=4, choices=TRADE_SIDES)
    order_type = models.CharField(verbose_name='Order Type', max_length=4, choices=ORDER_TYPES,
                                  default=ORDER_TYPES[0][0])
    fill_in_one = models.BooleanField(verbose_name='Fill In One', default=False)
    quantity_filled = models.PositiveIntegerField(verbose_name='Quantity Filled', default=0)

    @property
    def filled(self):
        return self.quantity_filled == self.quantity

    @property
    def quantity_unfilled(self):
        return self.quantity - self.quantity_filled

    objects = models.Manager()
    bidask = BidAskManager()

    def __str__(self):
        symbol = self.firm.symbol if self.firm else 'NONE'
        return f'<{symbol}> {self.side} {self.commodity}{self.contract} ({self.order_time})'

    class Meta:
        get_latest_by = 'order_time'
        ordering = ['order_time']


class PriceManager(models.Manager):
    """
    Custom price manager with support for getting latest price
    """

    def current_price(self, contract_code):
        """Gets latest transaction based on contract code"""
        return self.get_queryset().filter(commodity=contract_code[:2], contract=contract_code[-3:]).first()


class Transaction(models.Model):
    """Represents completed transaction between two firms"""
    uid = models.UUIDField(verbose_name='UID', primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    long_firm = models.ForeignKey(verbose_name='Long Firm', to='Firm', on_delete=models.CASCADE,
                                  related_name='long_firm')
    short_firm = models.ForeignKey(verbose_name='Short Firm', to='Firm', on_delete=models.CASCADE,
                                   related_name='short_firm')
    fill_time = models.DateTimeField(verbose_name='Fill Time', auto_now_add=True)
    commodity = models.CharField(verbose_name='Commodity', max_length=2, choices=get_commodity_choices())
    contract = models.CharField(verbose_name='Contract', max_length=4, validators=[validate_contract_code])
    price = models.DecimalField(verbose_name='Price', max_digits=8, decimal_places=3)
    quantity = models.PositiveIntegerField(verbose_name='Quantity')

    transactions = PriceManager()

    def __str__(self):
        return f'{self.quantity}x{self.commodity}{self.contract}@{self.price} ({self.fill_time})'

    class Meta:
        get_latest_by = 'fill_time'
        ordering = ['-fill_time', 'commodity', 'contract']
