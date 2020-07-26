from django.contrib import admin
from django.urls import path
from rest_framework.routers import DefaultRouter
from django.conf.urls import include

from . import views

router = DefaultRouter()
router.register(r'orderbook', views.OrderViewSet, basename='order')
router.register(r'bidask/(?P<commodity>.+)', views.BidAskViewSet, basename='bidask')

urlpatterns = [
    path('api/', include(router.urls)),
]

urlpatterns += [
    path('api/auth/', include('rest_framework.urls'))
]

admin.site.site_header = 'SCES Admin'
admin.site.site_title = 'Exchange Admin'
# admin.site.index_title = 'Welcome to SCES Admin'
