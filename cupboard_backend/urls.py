"""
URL configuration for cupboard_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import include, path
from rest_framework.versioning import NamespaceVersioning

from cupboard_app import auth0_authentication, v3_urls

versioning_class = NamespaceVersioning

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v3/', include((v3_urls, 'v3'), namespace='v3'))
]

# Auth0 Authentication
urlpatterns += [
    path('login', auth0_authentication.CLILoginAPIView.as_view(), name='cli_login'),
    path('logout', auth0_authentication.CLILogoutAPIView.as_view(), name='cli_logout'),
    path('refresh-token', auth0_authentication.RefreshTokenAPIView.as_view(), name='refresh_token')
]
