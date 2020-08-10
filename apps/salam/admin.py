from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin

from .forms import ExchangeUserCreationForm, ExchangeUserChangeForm
from .models import *


@admin.register(ExchangeUser)
class ExchangeUserAdmin(UserAdmin):
    add_form = ExchangeUserCreationForm
    form = ExchangeUserChangeForm
    model = ExchangeUser

    fieldsets = UserAdmin.fieldsets + ((None, {'fields': ('firm',)}),)
    add_fieldsets = UserAdmin.add_fieldsets + ((None, {'fields': ('email', 'firm',)}),)

    list_display = ['username', 'email', 'firm', ]


@admin.register(Firm)
class FirmAdmin(ModelAdmin):
    list_display = ['symbol', 'name', ]


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ['commodity', 'quantity', 'price', 'contract', 'side', 'firm', 'order_time']

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.firm:
            return [f.name for f in Order._meta.get_fields()]
        else:
            return []


@admin.register(Transaction)
class TransactionAdmin(ModelAdmin):
    list_display = ['commodity', 'contract', 'quantity', 'price', 'fill_time']

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['long_firm', 'short_firm', 'commodity', 'contract']
        else:
            return []
