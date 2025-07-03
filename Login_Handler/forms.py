from django import forms
from django.contrib.auth.models import User

class CustomUserCreationForm(forms.ModelForm):
    username = forms.CharField(label = 'Username', min_length = 5, max_length = 40)

    class Meta:
        model = User
        fields = ['username']
from django import forms

class CategoryForm(forms.Form):
    name = forms.CharField(label="Category Name",max_length=20)
