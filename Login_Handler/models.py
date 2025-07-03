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