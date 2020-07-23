from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('orderbook/', views.order_book, name='orderbook'),
    path('orderbook/<uuid:uid>', views.order_detail, name='order')
]