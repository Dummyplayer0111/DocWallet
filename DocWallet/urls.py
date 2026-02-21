from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Login_Handler.urls')),
    path('', include('Category_Handler.urls')),
    path('api/', include('Login_Handler.api_urls')),
    path('api/', include('Category_Handler.api_urls')),
]