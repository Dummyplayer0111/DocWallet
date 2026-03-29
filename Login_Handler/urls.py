from django.urls import path
from . import views

urlpatterns = [
    path('auth-receiver/', views.auth_receiver, name='auth_receiver'),
    path('oauth2-start/', views.oauth2_start, name='oauth2_start'),
]