"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions

# drf_yasg DRF Swagger Documentation config
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
        openapi.Info(
            title="Ecommerce Project Backend API drf_yasg Documentation",  # place any title here what you like
            default_version="v1",
            description="Swagger API Documentation for Ecommerce Project",
            terms_of_service="https://www.google.com/policies/terms/",
            contact=openapi.Contact(email="contact@snippets.local"),
            license=openapi.License(name="BSD License"),
        ),
        public=True,
        permission_classes=[permissions.AllowAny],
    )

# Using Django RestFramework official schemas
from rest_framework.schemas import get_schema_view
from rest_framework.documentation import include_docs_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include("authentication.urls")),
    path('admin_dashboard/', include("admin_dashboard.urls")),
    path('', include('users.urls')),
    path('orders/', include('orders.urls'))
]

if settings.DEBUG is True:
    urlpatterns += static(settings.MEDIA_URL, document_url=settings.MEDIA_ROOT)
    urlpatterns += [
        re_path(
            r"^swagger(?P<format>\.json|\.yaml)$",
            schema_view.without_ui(cache_timeout=0),
            name="schema-json",
        ),
        re_path(
            r"^swagger/$",
            schema_view.with_ui("swagger", cache_timeout=0),
            name="schema-swagger-ui",
        ),
        re_path(
            r"^redoc/$",
            schema_view.with_ui("redoc", cache_timeout=0),
            name="schema-redoc",
        ),
        # Django Restframework Official Documentation urls
        path(
            "schema/",
            get_schema_view(
                title="LetsProgramify Django Backend APIs",  # place any title here what you like
                description="API for LetsProgramify Django Backend",
                version="1.0.0",
            ),
            name="openapi-schema",
        ),
        path(
            "docs/",
            include_docs_urls(title="LetsProgramify Django Backend API Documentation"),
        ),
    ]
