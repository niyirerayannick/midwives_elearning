from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib import admin
from django.urls import path, include

# Swagger schema view configuration
schema_view = get_schema_view(
   openapi.Info(
      title="Midwives eLearning API",
      default_version='v2',
      description="API documentation for Midwives eLearning Platform",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@fcmc.muberarugo.org"),
      license=openapi.License(name="BSD License"),
   ),
    public=True,
   permission_classes=(permissions.AllowAny,), 
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    # Swagger URLs
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    # Optionally, include a JSON version of the schema for easier debugging
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]
