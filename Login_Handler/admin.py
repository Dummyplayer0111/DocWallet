from django.contrib import admin
from .models import GoogleCredentials,List_of_categories,User_Profile
admin.site.register(GoogleCredentials)
admin.site.register(List_of_categories)
admin.site.register(User_Profile)