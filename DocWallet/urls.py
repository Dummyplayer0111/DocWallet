from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Login_Handler.urls')),
    path('', include('Category_Handler.urls')),
]