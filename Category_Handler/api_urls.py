from django.urls import path
from . import api_views

urlpatterns = [
    path('bills/<str:uuid>/', api_views.bills, name='api_bills'),
    path('bill/', api_views.bill, name='api_bill'),
    path('bill/clean-edit/', api_views.clean_edit_bill, name='api_clean_edit_bill'),
    path('export/', api_views.export, name='api_export'),
    path('export/pdf/', api_views.export_pdf, name='api_export_pdf'),
    path('export/<str:uuid>/', api_views.export, name='api_export_uuid'),
]
