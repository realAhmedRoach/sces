from rest_framework import serializers
from apps.salam.models import Order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['uid', 'party', 'order_time', 'commodity', 'quantity', 'price', 'filled']