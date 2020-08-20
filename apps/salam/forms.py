from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import ExchangeUser


class ExchangeUserCreationForm(UserCreationForm):
    """Add firm to user creation"""
    class Meta:
        model = ExchangeUser
        fields = ('firm',)


class ExchangeUserChangeForm(UserChangeForm):
    """Add firm to user change"""
    class Meta:
        model = ExchangeUser
        fields = ('firm',)
