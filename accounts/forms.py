from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile

class RegisterForm(UserCreationForm):
    username = forms.CharField(
        max_length=20,
        label="Nazwa użytkownika",
        help_text="",  # Pusty napis — usuwa całkowicie tekst pomocniczy
        widget=forms.TextInput(attrs={'class': 'form-control', 'maxlength': '20'})
    )
    email = forms.EmailField(
        required=True, 
        label="Adres e-mail",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'np. jan@example.com'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'password1' in self.fields:
            self.fields['password1'].label = "Hasło"
            self.fields['password1'].help_text = "Hasło musi mieć co najmniej 8 znaków i nie może być zbyt powszechne."
            self.fields['password1'].widget.attrs.update({'class': 'form-control'})

        if 'password2' in self.fields:
            self.fields['password2'].label = "Potwierdzenie hasła"
            self.fields['password2'].help_text = "Wpisz dokładnie to samo hasło co powyżej w celu weryfikacji."
            self.fields['password2'].widget.attrs.update({'class': 'form-control'})

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(
        required=True, 
        label="Adres e-mail",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Imię',
            'last_name': 'Nazwisko',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'city', 'avatar', 'show_phone']
        labels = {
            'phone_number': 'Numer telefonu',
            'city': 'Miejscowość / Miasto',
            'avatar': 'Zdjęcie profilowe (Avatar)',
            'show_phone': 'Pokaż numer telefonu w ogłoszeniach',
        }
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'show_phone': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }