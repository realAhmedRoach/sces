from django.http import HttpResponse
from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.salam.permissions import IsOwner, WarehousePermissions
from apps.salam.serializers import *


def index(request):
    return HttpResponse('<a href="/api">API</a> - <a href="/admin">Admin</a>')


class NoDescriptionMixin:
    """
    Don't show view description in OPTIONS responses
    """

    def options(self, request, *args, **kwargs):
        """
        Don't include the view description in OPTIONS responses.
        """
        meta = self.metadata_class()
        data = meta.determine_metadata(request, self)
        data.pop('description')
        return Response(data, status=status.HTTP_200_OK)


class OrderViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   NoDescriptionMixin,
                   GenericViewSet):
    permission_classes = (IsAuthenticated, IsOwner,)
    lookup_field = 'uid'

    def get_queryset(self):
        return Order.objects.filter(firm=self.request.user.firm)

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return OrderDetailSerializer
        else:
            return OrderUpdateSerializer


class BidAskViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    lookup_field = 'commodity'
    lookup_url_kwarg = 'commodity'
    serializer_class = BidAskSerializer

    def get_queryset(self):
        if self.lookup_url_kwarg in self.kwargs:
            contract_code = self.kwargs[self.lookup_url_kwarg]
            bid = Order.bidask.best_bid(contract_code=contract_code)
            ask = Order.bidask.best_ask(contract_code=contract_code)
            if bid and ask:
                return [bid, ask]

    def list(self, request, *args, **kwargs):
        serializer = CommoditiesSerializer(Order.objects.none(), context={'request': request, 'view': 'bidask-list'})
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)


class PriceViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    lookup_field = 'commodity'
    lookup_url_kwarg = 'commodity'
    serializer_class = PriceSerializer

    def get_queryset(self):
        if self.lookup_url_kwarg in self.kwargs:
            contract_code = self.kwargs[self.lookup_url_kwarg]
            current_price = Transaction.transactions.current_price(contract_code=contract_code)
            return current_price

    def list(self, request, *args, **kwargs):
        serializer = CommoditiesSerializer(Transaction.transactions.none(),
                                           context={'request': request, 'view': 'price-list'})
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        qs = self.get_queryset()
        if qs:
            serializer = self.get_serializer(self.get_queryset(), many=False)
            return Response(serializer.data)
        else:
            return Response([])


class WarehouseReceiptViewSet(mixins.CreateModelMixin,
                              mixins.RetrieveModelMixin,
                              mixins.DestroyModelMixin,
                              mixins.ListModelMixin,
                              mixins.UpdateModelMixin,
                              NoDescriptionMixin,
                              GenericViewSet):
    lookup_field = 'uid'
    permission_classes = (WarehousePermissions,)

    def get_queryset(self):
        return WarehouseReceipt.receipts.get_filtered_queryset(self.request.user.firm)

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return WarehouseReceiptDetailSerializer
        else:
            return WarehouseReceiptUpdateSerializer
