from rest_framework import serializers

from apps.salam.models import Order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['uid', 'order_time', 'commodity', 'quantity', 'price', 'filled']


class NewOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
