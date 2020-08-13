from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('apps.salam.urls')),
    path('admin/', admin.site.urls),
]

admin.site.site_header = 'SCES Admin'
admin.site.site_title = 'Exchange Admin'
