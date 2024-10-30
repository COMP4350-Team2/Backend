from django.urls import path

from cupboard_app.views import (
    PublicMessageAPIView,
    PrivateMessageAPIView,
    PrivateScopedMessageAPIView,
    IngredientsViewSet,
    UserViewSet,
    ListIngredientViewSet,
    UserListIngredientsViewSet
)

urlpatterns = [
    # urlpaths should have names for ease of testing
    path('api/public', PublicMessageAPIView.as_view(), name='public'),
    path('api/private', PrivateMessageAPIView.as_view(), name='private'),
    path('api/private_scoped', PrivateScopedMessageAPIView.as_view(), name='private_scoped'),
    path('api/user', UserViewSet.as_view({'post': 'create'}), name='user'),
    path(
        'api/get_all_ingredients',
        IngredientsViewSet.as_view({'get': 'list'}),
        name='ingredients'
    ),
    path(
        'api/user_list_ingredients',
        UserListIngredientsViewSet.as_view({'get': 'list', 'put': 'update'}),
        name='user_list_ingredients'
    ),
    path(
        'api/user_list_ingredients/<str:list_name>',
        UserListIngredientsViewSet.as_view(
            {'get': 'retrieve', 'post': 'create', 'delete': 'destroy'}
        ),
        name='specific_user_list_ingredients'
    ),
    path(
        'api/user_list_ingredients/add_ingredient',
        ListIngredientViewSet.as_view({'post': 'create'}),
        name='add_ingredient'
    ),
    path(
        'api/user_list_ingredients/set_ingredient',
        ListIngredientViewSet.as_view({'put': 'update'}),
        name='set_ingredient'
    ),
    path(
        'api/user_list_ingredients/delete_ingredient',
        ListIngredientViewSet.as_view({'delete': 'destroy'}),
        name='delete_ingredient'
    ),
]
