from rest_framework import serializers

from apps.salam.models import Order


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

    class Meta:
        model = Order
        fields = '__all__'


class BidAskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['commodity', 'price', 'quantity', 'side']


class CommoditiesSerializer(serializers.ModelSerializer):
    commodities = serializers.SerializerMethodField()

    def get_commodities(self, obj):
        choices = [choice for choice in Order._meta.get_field('commodity').choices]
        choice_urls = {choice[1]: 'http://127.0.0.1:8000/api/bidask/%s' % choice[0] for choice in choices}
        return choice_urls

    class Meta:
        model = Order
        fields = ['commodities']
