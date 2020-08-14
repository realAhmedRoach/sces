from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse

from django.utils.translation import gettext_lazy as _

from apps.salam.models import Order, Transaction, WarehouseReceipt
from sces.commodity import get_valid_contracts
from apps.salam.validators import validate_contract_code


class CurrentUserFirmDefault:
    requires_context = True

    def __call__(self, serializer_field):
        return serializer_field.context['request'].user.firm

    def __repr__(self):
        return '%s()' % self.__class__.__name__


class OrderSerializer(serializers.ModelSerializer):
    firm = serializers.HiddenField(default=CurrentUserFirmDefault())

    def update(self, instance, validated_data):
        validated_data.pop('firm')
        return super(OrderSerializer, self).update(instance, validated_data)

    def create(self, validated_data):
        return super(OrderSerializer, self).create(validated_data)

    def validate_contract(self, value):
        validate_contract_code(value)
        return value

    class Meta:
        model = Order
        fields = '__all__'
        extra_kwargs = {'contract': {'choices': get_valid_contracts()}}


class BidAskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['commodity', 'price', 'quantity', 'contract', 'side']


class CommoditiesSerializer(serializers.ModelSerializer):
    commodities = serializers.SerializerMethodField()

    def get_commodities(self, obj):
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