from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse

from apps.salam.models import Order, Transaction, WarehouseReceipt
from apps.salam.validators import validate_contract_code
from sces.commodity import get_valid_contracts


class CurrentUserFirmDefault:
    """
    A field default which returns the current users firm
    """
    requires_context = True

    def __call__(self, serializer_field):
        return serializer_field.context['request'].user.firm

    def __repr__(self):
        return '%s()' % self.__class__.__name__


class OrderSerializer(serializers.ModelSerializer):
    firm = serializers.HiddenField(default=CurrentUserFirmDefault())

    def validate_contract(self, value):
        validate_contract_code(value)
        return value

    class Meta:
        model = Order
        exclude = ['quantity_filled']
        extra_kwargs = {'contract': {'choices': get_valid_contracts()}}


class BidAskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['commodity', 'price', 'quantity', 'contract', 'side']


class CommoditiesSerializer(serializers.ModelSerializer):
    """
    Serializes all commodities and available contracts
    """
    commodities = serializers.SerializerMethodField()

    def get_commodities(self, obj):
        # TODO: choices will possibly be no longer available for contracts
        choices = [choice for choice in Order._meta.get_field('commodity').choices]
        contracts = [contract for contract in Order._meta.get_field('contract').choices]
        baseurl = reverse(self.context['view'], request=self.context['request'])
        choice_urls = {choice[1]: {
            contract[1]: '%s%s%s' % (baseurl, choice[0], contract[0]) for contract in contracts
        } for choice in choices}
        return choice_urls

    class Meta:
        model = Order
        fields = ['commodities']


class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['fill_time', 'commodity', 'contract', 'price']


class WarehouseReceiptDetailSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, obj):
        return reverse('warehouse-detail', args=[obj.uid], request=self.context['request'])

    class Meta:
        model = WarehouseReceipt
        fields = '__all__'


class WarehouseReceiptUpdateSerializer(serializers.ModelSerializer):
    warehouse = serializers.HiddenField(default=CurrentUserFirmDefault())

    def validate(self, attrs):
        if attrs['firm'] == attrs['warehouse']:
            raise ValidationError(_('The warehouse cannot own a commodity in its own location'))
        return attrs

    class Meta:
        model = WarehouseReceipt
        fields = '__all__'