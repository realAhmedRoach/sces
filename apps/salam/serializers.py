from rest_framework import serializers
from rest_framework.reverse import reverse

from apps.salam.models import Order
from commodity import get_valid_contracts
from validators import validate_contract_code


class CurrentUserPartyDefault:
    requires_context = True

    def __call__(self, serializer_field):
        return serializer_field.context['request'].user.party

    def __repr__(self):
        return '%s()' % self.__class__.__name__


class OrderSerializer(serializers.ModelSerializer):
    party = serializers.HiddenField(default=CurrentUserPartyDefault())

    def update(self, instance, validated_data):
        validated_data.pop('party')
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
        baseurl = reverse('bidask-list', request=self.context['request'])
        choice_urls = {choice[1]: {
            contract[1]: '%s%s%s' % (baseurl, choice[0], contract[0]) for contract in contracts
        } for choice in choices}
        return choice_urls

    class Meta:
        model = Order
        fields = ['commodities']
