from rest_framework import permissions
from rest_framework import viewsets

from apps.salam.models import Order
from apps.salam.permissions import IsOwnerOrReadOnly
from apps.salam.serializers import OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    lookup_field = 'uid'
