from django import forms
from django.contrib.auth.models import User
import pytz
from Login_Handler.models import List_of_categories

class CustomUserCreationForm(forms.ModelForm):
    username = forms.CharField(label = 'Username', min_length = 5, max_length = 40,required=True)
    timezone = forms.ChoiceField(choices=[(tz, tz) for tz in pytz.common_timezones],label='Select Timezone',initial='UTC',required=True)
    class Meta:
        model = User
        fields = ['username']

class CategoryForm(forms.Form):
    name = forms.CharField(label="Category Name",min_length=3,max_length=20,required=True)

class ImageUploadForm(forms.Form):
    image = forms.ImageField(required=True)
    value = forms.DecimalField(max_digits=11, decimal_places=2,min_value=0.01,required=True)

class TimeframeForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}),required=True)
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}),required=True)
    categories = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,required=True)
    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, **kwargs)
        user = request.user if request else None
        if user and user.is_authenticated:
            try:
                obj = List_of_categories.objects.get(user=user)
                self.fields['categories'].choices = [(c, c) for c in obj.categories]
            except List_of_categories.DoesNotExist:
                self.fields['categories'].choices = []
        else:
            self.fields['categories'].choices = []

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['start_date'] > cleaned_data['end_date']:
            raise forms.ValidationError("Start date must be before or equal to end date.")
        
class TimeframeForm_2(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}),required=True)
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}),required=True)
    
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['start_date'] > cleaned_data['end_date']:
            raise forms.ValidationError("Start date must be before or equal to end date.")
        

class EditUploadForm(forms.Form):
    value = forms.DecimalField(max_digits=11, decimal_places=2,min_value=0.01,required=True)


class ImageUploadForm_2(forms.Form):
    image = forms.ImageField(required=True)
    value = forms.DecimalField(max_digits=11, decimal_places=2,min_value=0.01,required=True)
    category = forms.ChoiceField(required=True)
    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, **kwargs)
        user = request.user if request else None
        if user and user.is_authenticated:
            try:
                obj = List_of_categories.objects.get(user=user)
                self.fields['category'].choices = [(c, c) for c in obj.categories]
            except List_of_categories.DoesNotExist:
                self.fields['category'].choices = []
        else:
            self.fields['category'].choices = []