from django import forms
from django.contrib.auth.models import User
import pytz

class CustomUserCreationForm(forms.ModelForm):
    username = forms.CharField(label = 'Username', min_length = 5, max_length = 40)
    timezone = forms.ChoiceField(choices=[(tz, tz) for tz in pytz.common_timezones],label='Select Timezone',initial='UTC')
    class Meta:
        model = User
        fields = ['username']

class CategoryForm(forms.Form):
    name = forms.CharField(label="Category Name",max_length=100)

class ImageUploadForm(forms.Form):
    image = forms.ImageField()
    value = forms.DecimalField(max_digits=10, decimal_places=2)
