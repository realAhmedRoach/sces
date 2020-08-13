from django.contrib import admin
from django.urls import path
from rest_framework.routers import DefaultRouter
from django.conf.urls import include

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

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
    path('api/auth/', include('rest_framework.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
