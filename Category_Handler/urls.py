from django.urls import path
from . import views

urlpatterns = [
    path('View-Category/<str:UUID>', views.inside_category, name ='view_category'),
    path('In-Category/Add-Bill/<str:UUID>', views.add, name="new_bill"),
    path('Export', views.export, name="choose_time_frame"),
    path('Export/Download-PDF/<int:rows>', views.download, name="download"),
    path('In-Category/Export-Bills/<str:UUID>', views.add, name="export_bills"),
    path('In-Category/Export/<str:UUID>', views.export, name="cat_timeframe"),
    path('In-Category/View_Bill/', views.view_bill, name='bill'),
    path('In-Category/Edit_Bill/', views.edit_bill, name='edit_bill'),
    path('In-Category/Clean_Edit_Bill/', views.clean_edit_bill, name='clean_edit_bill'),
]