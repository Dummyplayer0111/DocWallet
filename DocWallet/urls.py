from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Login_Handler.urls')),
    path('', include('Category_Handler.urls')),
    path('api/', include('Login_Handler.api_urls')),
    path('api/', include('Category_Handler.api_urls')),
    re_path(r'^(?!api/|admin/|static/).*$', TemplateView.as_view(template_name='index.html')),
]