from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Article


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'text', 'image', 'category']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Article title',
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-input form-textarea',
                'placeholder': 'Write your article...',
                'rows': 16,
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-input',
            }),
            'category': forms.Select(attrs={
                'class': 'form-input',
            }),
        }
