from django.urls import path

from . import views

urlpatterns = [
    path('api/public', views.public),
    path('api/private', views.private),
    path('api/private-scoped', views.private_scoped),
    path('api/get_all_ingredients', views.get_all_ingredients, name="get_all_ingredients")
]
