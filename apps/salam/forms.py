from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import ExchangeUser


class ExchangeUserCreationForm(UserCreationForm):

    class Meta:
        model = ExchangeUser
        fields = ('firm',)


class ExchangeUserChangeForm(UserChangeForm):

    class Meta:
        model = ExchangeUser
        fields = ('firm',)
