from django.urls import path
from . import views

urlpatterns = [
    path('View-Category/<str:UUID>', views.inside_category, name ='view_category'),
    path('In-Category/Add-Bill/<str:UUID>', views.add, name="new_bill")
]