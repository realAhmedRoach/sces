from rest_framework import serializers
from rest_framework.reverse import reverse

from apps.salam.models import Order, Transaction
from sces.commodity import get_valid_contracts
from apps.salam.validators import validate_contract_code


class CurrentUserPartyDefault:
    requires_context = True

    def __call__(self, serializer_field):
        return serializer_field.context['request'].user.firm

    def __repr__(self):
        return '%s()' % self.__class__.__name__


class OrderSerializer(serializers.ModelSerializer):
    party = serializers.HiddenField(default=CurrentUserPartyDefault())

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

    def __init__(self, *args, **kwargs):
        super(CommoditiesSerializer, self).__init__(*args, **kwargs)

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
