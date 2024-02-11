from typing import Any
from django.forms import ModelForm,CharField,EmailField,PasswordInput,ImageField,TextInput, ValidationError
from app.models import CustomUser
from django.forms import forms



class UserProfileForm(forms.Form):
    username = CharField(max_length=32,min_length=3,required=True,label='Имя пользователя')
    email = EmailField(required=True,label='Почта')
    avatar = ImageField(required=False,label='PFP')

class PasswordChangeForm(forms.Form):
    password_reset_email = EmailField(required=False,widget=TextInput(attrs={
        'placeholder':'Введите почту от аккаунта для изменения пароля',
    }),label='Почта для изменения пароля')