from django.urls import path
from . import views

urlpatterns = [
    path('', views.sign_in, name='sign_in'),
    path('auth-receiver/', views.auth_receiver, name='auth_receiver'),
    path('choose-name/', views.choose_name, name = 'choose_name'),
    path('home/', views.home, name = 'home'),
    path('oauth2-start/', views.oauth2_start, name='oauth2_start'),
    path('home/edit-categories/', views.edit, name ='edit'),
    path('home/edit-categories/<int:category_id>/', views.edit, name ='edit'),
    path('home/edit-categories/add/', views.add, name ='add'),
    path('home/edit-categories/rename/<int:category_id>/', views.rename, name ='rename'),
]