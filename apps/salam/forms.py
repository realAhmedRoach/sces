from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import ExchangeUser, Party


class ExchangeUserCreationForm(UserCreationForm):

    class Meta:
        model = ExchangeUser
        fields = ('username', 'email', 'party')


class ExchangeUserChangeForm(UserChangeForm):

    class Meta:
        model = ExchangeUser
        fields = ('username', 'email', 'party')
