from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import ExchangeUserCreationForm, ExchangeUserChangeForm
from .models import *


class ExchangeUserAdmin(UserAdmin):
    add_form = ExchangeUserCreationForm
    form = ExchangeUserChangeForm
    model = ExchangeUser

    fieldsets = UserAdmin.fieldsets + ((None, {'fields': ('party',)}),)
    add_fieldsets = UserAdmin.add_fieldsets + ((None, {'fields': ('email', 'party',)}),)

    list_display = ['username', 'email', 'party', ]


class PartyAdmin(ModelAdmin):
    list_display = ['symbol', 'name', ]


class OrderAdmin(ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['party']
        else:
            return []


admin.site.register(ExchangeUser, ExchangeUserAdmin)

admin.site.register(Party, PartyAdmin)
admin.site.register(Order, OrderAdmin)
