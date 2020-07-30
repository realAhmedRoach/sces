from django.http import HttpResponse
from rest_framework import permissions, mixins, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.salam.models import Order
from apps.salam.permissions import IsOwnerOrReadOnly
from apps.salam.serializers import OrderSerializer, BidAskSerializer, CommoditiesSerializer


def index(request):
    return HttpResponse('<a href="/api">API</a>')


class OrderViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    lookup_field = 'uid'

    def get_queryset(self):
        return Order.objects.filter(party=self.request.user.party)

    def options(self, request, *args, **kwargs):
        """
        Don't include the view description in OPTIONS responses.
        """
        meta = self.metadata_class()
        data = meta.determine_metadata(request, self)
        data.pop('description')
        return Response(data, status=status.HTTP_200_OK)


class BidAskViewSet(mixins.ListModelMixin, GenericViewSet):
    lookup_field = 'commodity'
    lookup_url_kwarg = 'commodity'
    serializer_class = BidAskSerializer

    # TODO: show commodity options in homepage
    def get_queryset(self):
        queryset = []
        if self.lookup_url_kwarg in self.kwargs:
            contract_code = self.kwargs[self.lookup_url_kwarg]
            bid = Order.bidask.bid(contract_code=contract_code)
            ask = Order.bidask.ask(contract_code=contract_code)
            if bid and ask:
                queryset = [bid, ask]
            else:
                queryset = Order.objects.none()
        return queryset

    def list(self, request, *args, **kwargs):
        if self.lookup_url_kwarg in self.kwargs:
            serializer = self.get_serializer(self.get_queryset(), many=True)
            return Response(serializer.data)
        else:
            serializer = CommoditiesSerializer(Order.objects.none(), context={'request': request})
            return Response(serializer.data)
