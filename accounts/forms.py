from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Adres e-mail")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True, label="Adres e-mail")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'city', 'avatar', 'show_phone']