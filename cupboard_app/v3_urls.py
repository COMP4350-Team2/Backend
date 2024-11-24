from django.urls import path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView
)

from cupboard_app.views import (
    IngredientsViewSet,
    MeasurementsViewSet,
    UserViewSet,
    UserListIngredientsViewSet,
    UpdateUserListIngredientsViewSet,
    CustomIngredientsViewSet
)

"""
URL order matters! The more granular it is, it should be on top of other urls.
i.e. user_list_ingredients/add_ingredient should come before user_list_ingredients
"""
urlpatterns = [
    # urlpaths should have names for ease of testing
    path('user', UserViewSet.as_view({'post': 'create'}), name='user'),
    path('ingredients', IngredientsViewSet.as_view({'get': 'list'}), name='ingredients'),
    path('measurements', MeasurementsViewSet.as_view({'get': 'list'}), name='measurements'),
    path(
        'user/lists/<str:list_name>/ingredients/<str:ingredient>/units/<str:unit>',
        UpdateUserListIngredientsViewSet.as_view({'delete': 'destroy'}),
        name='delete_ingredient'
    ),
    path(
        'user/lists/ingredients',
        UpdateUserListIngredientsViewSet.as_view(
            {'post': 'create', 'patch': 'update'}
        ),
        name='add_set_ingredients'
    ),
    path(
        'user/customingredients',
        CustomIngredientsViewSet.as_view(
            {'post': 'create', 'delete': 'destroy'}
        ),
        name='add_delete_customingredient'
    ),
    path(
        'user/lists/<str:list_name>',
        UserListIngredientsViewSet.as_view(
            {'get': 'retrieve', 'post': 'create', 'delete': 'destroy'}
        ),
        name='specific_user_list_ingredients'
    ),
    path(
        'user/lists',
        UserListIngredientsViewSet.as_view({'get': 'list', 'put': 'update'}),
        name='user_list_ingredients'
    )
]

# API Documentation versions
urlpatterns += [
    path('schema/', SpectacularAPIView.as_view(), name='schema-v3'),
    path('doc/', SpectacularSwaggerView.as_view(url_name='schema-v3'), name='swagger-ui-v3'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema-v3'), name='redoc-v3'),
]
