from django.urls import path

from . import views

urlpatterns = [
    # urlpaths should have names for ease of testing
    path('api/public', views.public, name='public'),
    path('api/private', views.private, name='private'),
    path('api/private-scoped', views.private_scoped, name='private-scoped'),
]
