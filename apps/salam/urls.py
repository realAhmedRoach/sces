from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls import include

from . import views

urlpatterns = [
    path('', views.api_root),
    path('orderbook/', views.OrderList.as_view(), name='orderbook'),
    path('orderbook/<uuid:uid>', views.OrderDetail.as_view(), name='order')
]

urlpatterns = format_suffix_patterns(urlpatterns)

urlpatterns += [
    path('api-auth/', include('rest_framework.urls'))
]
