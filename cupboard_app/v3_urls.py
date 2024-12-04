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
    CustomIngredientsViewSet,
    RecipeViewSet,
    RecipeIngredientsViewSet,
    RecipeStepsViewSet
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
        'user/lists/ingredients',
        UpdateUserListIngredientsViewSet.as_view(
            {'post': 'create', 'patch': 'update', 'delete': 'destroy'}
        ),
        name='edit_user_list_ingredients'
    ),
    path(
        'user/ingredients/custom',
        CustomIngredientsViewSet.as_view(
            {'post': 'create'}
        ),
        name='custom_ingredient'
    ),
    path(
        'user/ingredients/custom/<str:ingredient>',
        CustomIngredientsViewSet.as_view(
            {'delete': 'destroy'}
        ),
        name='specific_custom_ingredient'
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
    ),
    path(
        'user/recipe/<str:recipe_name>/ingredient',
        RecipeIngredientsViewSet.as_view({'post': 'create', 'delete': 'destroy'}),
        name='recipe_ingredients'
    ),
    path(
        'user/recipe/<str:recipe_name>/step',
        RecipeStepsViewSet.as_view({'post': 'create', 'patch': 'update', 'delete': 'destroy'}),
        name='recipe_steps'
    ),
    path(
        'user/recipe/<str:recipe_name>',
        RecipeViewSet.as_view({'get': 'retrieve', 'post': 'create', 'delete': 'destroy'}),
        name='specific_recipe'
    ),
    path(
        'user/recipe',
        RecipeViewSet.as_view({'get': 'list'}),
        name='recipe'
    )
]

# API Documentation versions
urlpatterns += [
    path('schema/', SpectacularAPIView.as_view(), name='schema-v3'),
    path('doc/', SpectacularSwaggerView.as_view(url_name='schema-v3'), name='swagger-ui-v3'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema-v3'), name='redoc-v3'),
]
