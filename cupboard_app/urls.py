from django.urls import path

from cupboard_app.views import (
    PublicMessageAPIView,
    PrivateMessageAPIView,
    PrivateScopedMessageAPIView,
    AllIngredientsAPIView,
    UserAPIView,
    ListItemAPIView
)

urlpatterns = [
    # urlpaths should have names for ease of testing
    path('api/public', PublicMessageAPIView.as_view(), name='public'),
    path('api/private', PrivateMessageAPIView.as_view(), name='private'),
    path('api/private_scoped', PrivateScopedMessageAPIView.as_view(), name='private_scoped'),
    path('api/get_all_ingredients', AllIngredientsAPIView.as_view(), name="get_all_ingredients"),
    path('api/user', UserAPIView.as_view(), name="user"),
    path('api/list_item', ListItemAPIView.as_view(), name="list_item"),
]
