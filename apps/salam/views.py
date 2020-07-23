from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from apps.salam.models import Order
from apps.salam.serializers import OrderSerializer, NewOrderSerializer


def home(request):
    return HttpResponse("Salam")


@csrf_exempt
def order_book(request):
    """
    List all orders or create a new order
    """
    if request.method == 'GET':
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = OrderSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)


@csrf_exempt
def order_detail(request, uid):
    """
    Retrieve or delete an order.
    """
    try:
        order = Order.objects.get(uid=uid)
    except Order.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = OrderSerializer(order)
        return JsonResponse(serializer.data)

    elif request.method == 'DELETE':
        order.delete()
        return HttpResponse(status=204)
