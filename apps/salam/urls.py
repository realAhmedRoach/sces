from django.contrib import admin
from django.urls import path
from rest_framework.routers import DefaultRouter
from django.conf.urls import include

from . import views

router = DefaultRouter()

router.get_api_root_view().cls.__name__ = 'Commodity Exchange'
router.get_api_root_view().cls.__doc__ = 'View/create orders or view current bid/ask'

router.register(r'orderbook', views.OrderViewSet, basename='order')
router.register(r'bidask', views.BidAskViewSet, basename='bidask')
router.register(r'price', views.PriceViewSet, basename='price')
# router.register(r'bidask/(?P<commodity>.+)', views.BidAskViewSet, basename='bidask')

urlpatterns = [
    path('', views.index),
    path('api/', include(router.urls)),
    path('api/auth/', include('rest_framework.urls'))
]

admin.site.site_header = 'SCES Admin'
admin.site.site_title = 'Exchange Admin'
# admin.site.index_title = 'Welcome to SCES Admin'
