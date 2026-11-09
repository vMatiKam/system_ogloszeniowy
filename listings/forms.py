from django import forms
from .models import Listing, PrivateMessage, ListingComment


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'category', 'description', 'price', 'is_negotiable', 'condition', 'location', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'np. Rower górski Trek'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Pozostaw puste, jeśli za darmo'}),
            'condition': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'np. Warszawa'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }


class MessageForm(forms.ModelForm):
    class Meta:
        model = PrivateMessage
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Wpisz treść wiadomości do ogłoszeniodawcy...'
            }),
        }
        labels = {
            'content': 'Treść wiadomości'
        }


class ListingCommentForm(forms.ModelForm):
    class Meta:
        model = ListingComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Napisz komentarz lub zadaj pytanie dotyczące oferty...'
            }),
        }
        labels = {
            'content': 'Twój komentarz'
        }