from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls import include

from . import views

router = DefaultRouter()
router.register(r'orderbook', views.OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

urlpatterns += [
    path('api-auth/', include('rest_framework.urls'))
]
