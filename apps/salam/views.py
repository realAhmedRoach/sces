from rest_framework import permissions, mixins
from rest_framework.viewsets import GenericViewSet

from apps.salam.models import Order
from apps.salam.permissions import IsOwnerOrReadOnly
from apps.salam.serializers import OrderSerializer


class OrderViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    lookup_field = 'uid'

    def get_queryset(self):
        party = self.request.user.party
        return Order.objects.filter(party=party)
