from rest_framework import serializers

from apps.salam.models import Order


class OrderSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data):
        validated_data.pop('party')
        return super(OrderSerializer, self).update(instance, validated_data)

    class Meta:
        model = Order
        fields = '__all__'
