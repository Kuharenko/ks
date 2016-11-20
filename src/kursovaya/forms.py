# -*- coding: utf8 -*-

from django import forms
from django.contrib.auth.models import User
import re


class myForm(forms.Form):
    text = forms.CharField( max_length=20000, widget= forms.Textarea(attrs={'class': 'form-control'}))


class RegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']
        labels = {
            'username': 'Пользователь',
            'password': 'Пароль'
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'})
        }

    def clean_username(self):
        name = self.cleaned_data['username']
        z = re.search('^[a-zA-Z0-9]+$', name)
        if z is None:
            raise forms.ValidationError("Имя пользователя может содержать только буквы и цифры!")
        return name


class LoginForm(forms.Form):
    username = forms.CharField(max_length=200)
    password = forms.PasswordInput()