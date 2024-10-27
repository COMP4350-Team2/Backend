from django.urls import path

from cupboard_app.views import (
    PublicMessageAPIView,
    PrivateMessageAPIView,
    PrivateScopedMessageAPIView,
    AllIngredientsAPIView,
    UserAPIView,
    UserListIngredientsAPIView
)

urlpatterns = [
    # urlpaths should have names for ease of testing
    path('api/public', PublicMessageAPIView.as_view(), name='public'),
    path('api/private', PrivateMessageAPIView.as_view(), name='private'),
    path('api/private_scoped', PrivateScopedMessageAPIView.as_view(), name='private_scoped'),
    path('api/get_all_ingredients', AllIngredientsAPIView.as_view(), name="get_all_ingredients"),
    path('api/user', UserAPIView.as_view(), name="user"),
    path(
        'api/user_list_ingredients',
        UserListIngredientsAPIView.as_view(),
        name="user_list_ingredients"
    ),
]
