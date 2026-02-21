from django.urls import path
from . import api_views

urlpatterns = [
    path('auth/status/', api_views.auth_status, name='api_auth_status'),
    path('auth/logout/', api_views.auth_logout, name='api_auth_logout'),
    path('auth/timezones/', api_views.timezones, name='api_timezones'),
    path('categories/', api_views.categories, name='api_categories'),
    path('categories/<int:category_id>/', api_views.category_detail, name='api_category_detail'),
    path('choose-name/', api_views.choose_name, name='api_choose_name'),
]
