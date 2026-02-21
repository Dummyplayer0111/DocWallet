from django.db import models
from django.contrib.auth.models import User

class GoogleCredentials(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.TextField(null=True, blank=True)
    refresh_token = models.TextField(null=True, blank=True)
    token_uri = models.CharField(max_length=255, null=True, blank=True)
    scopes = models.TextField(null=True, blank=True)
    expiry = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

class List_of_categories(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    categories = models.JSONField(default=list)

class User_Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    timezone = models.CharField(max_length=100, default='UTC')

    def __str__(self):
        return f"{self.user.username}'s profile with timezone {self.timezone}"

