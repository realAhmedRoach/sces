from django.urls import path
from rest_framework.routers import DefaultRouter
from django.conf.urls import include

from . import views

router = DefaultRouter()
router.register(r'orderbook', views.OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
]

urlpatterns += [
    path('api-auth/', include('rest_framework.urls'))
]
