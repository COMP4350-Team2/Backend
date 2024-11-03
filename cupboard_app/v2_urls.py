from django.urls import path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView
)

from cupboard_app.views import (
    PublicMessageAPIView,
    PrivateMessageAPIView,
    PrivateScopedMessageAPIView,
    IngredientsViewSet,
    MeasurementsViewSet,
    UserViewSet,
    UserListIngredientsViewSet,
    UpdateUserListIngredientsViewSet,
)

"""
URL order matters! The more granular it is, it should be on top of other urls.
i.e. user_list_ingredients/add_ingredient should come before user_list_ingredients
"""
urlpatterns = [
    # urlpaths should have names for ease of testing
    path('public', PublicMessageAPIView.as_view(), name='public'),
    path('private', PrivateMessageAPIView.as_view(), name='private'),
    path('private_scoped', PrivateScopedMessageAPIView.as_view(), name='private_scoped'),
    path('user', UserViewSet.as_view({'post': 'create'}), name='user'),
    path(
        'get_all_ingredients',
        IngredientsViewSet.as_view({'get': 'list'}),
        name='get_all_ingredients'
    ),
    path(
        'get_all_measurements',
        MeasurementsViewSet.as_view({'get': 'list'}),
        name='get_all_measurements'
    ),
    path(
        'user_list_ingredients/add_ingredient',
        UpdateUserListIngredientsViewSet.as_view({'put': 'create'}),
        name='add_ingredient'
    ),
    path(
        'user_list_ingredients/set_ingredient',
        UpdateUserListIngredientsViewSet.as_view({'put': 'update'}),
        name='set_ingredient'
    ),
    path(
        'user_list_ingredients/delete_ingredient',
        UpdateUserListIngredientsViewSet.as_view({'put': 'destroy'}),
        name='delete_ingredient'
    ),
    path(
        'user_list_ingredients',
        UserListIngredientsViewSet.as_view({'get': 'list', 'put': 'update'}),
        name='user_list_ingredients'
    ),
    path(
        'user_list_ingredients/<str:list_name>',
        UserListIngredientsViewSet.as_view(
            {'get': 'retrieve', 'post': 'create', 'delete': 'destroy'}
        ),
        name='specific_user_list_ingredients'
    ),
]

# API Documentation versions
urlpatterns += [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema-v2'),
    path('doc/', SpectacularSwaggerView.as_view(url_name='schema-v2'), name='swagger-ui-v2'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema-v2'), name='redoc-v2'),
]
