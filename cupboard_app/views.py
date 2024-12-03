from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import (
    extend_schema,
    inline_serializer,
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse
)
from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.views import exception_handler

from utils.api_helper import (
    get_auth_username_from_payload,
    get_auth_email_from_payload
)
from cupboard_app.exceptions import MissingInformation
from cupboard_app.queries import (
    add_default_user_lists,
    create_user,
    create_list_name,
    create_user_list_ingredients,
    delete_user_list_ingredients,
    create_custom_ingredient,
    delete_custom_ingredient,
    get_all_ingredients,
    get_all_custom_ingredients,
    get_all_measurements,
    get_user_lists_ingredients,
    get_specific_user_lists_ingredients,
    add_list_ingredient,
    delete_list_ingredient,
    set_list_ingredient,
    change_user_list_ingredient_name,
    add_ingredient_to_recipe,
    remove_ingredient_from_recipe,
    add_step_to_recipe,
    remove_step_from_recipe,
    edit_step_in_recipe,
    get_all_recipes,
    create_recipe,
    get_recipe,
    delete_recipe,
    INVALID_USER_LIST,
    INVALID_RECIPE,
    MAX_LISTS_PER_USER
)
from cupboard_app.serializers import (
    MessageSerializer,
    IngredientSerializer,
    MeasurementSerializer,
    UserSerializer,
    UserListIngredientsSerializer,
    CustomIngredientSerializer,
    RecipeSerializer
)

INVALID_TOKEN = {'message': 'Given token not valid for any token type'}
NO_AUTH = {'message': 'Authentication credentials were not provided.'}
PERMISSION_DENIED = {
    'message': 'Permission denied. You do not have permission to perform this action.'
}
REQUIRED_VALUE_MISSING = (
    'Required value missing from sent request, '
    'please ensure all items are sent in the following format: '
)

INGREDIENTS = [
    {
        'ingredient_name': 'Beef',
        'ingredient_type': 'Meat',
        'amount': 500,
        'unit': 'g',
        'is_custom_ingredient': False
    },
    {
        'ingredient_name': '2% Milk',
        'ingredient_type': 'Dairy',
        'amount': 2,
        'unit': 'L',
        'is_custom_ingredient': False
    },
    {
        'ingredient_name': 'Homemade Meatball',
        'ingredient_type': 'Meat',
        'amount': 25,
        'unit': 'count',
        'is_custom_ingredient': True
    }
]
STEPS = [
    'Step one of my recipe!',
    'Step two of my recipe!',
    'Final step of my recipe!'
]
GROCERY_LIST = {
    'user': 'teacup',
    'list_name': 'Grocery',
    'ingredients': INGREDIENTS
}
FRIDGE_LIST = {
    'user': 'teacup',
    'list_name': 'Fridge',
    'ingredients': INGREDIENTS
}
SINGLE_CUSTOM_INGREDIENT_DICT = {
    'user': 'teacup',
    'name': 'Beef',
    'type': 'Meat'
}
SINGLE_RECIPE = {
    'user': 'teacup',
    'recipe_name': 'my_recipe',  
    'ingredients': INGREDIENTS,
    'steps': STEPS
}


# OpenAPI response types
auth_failed_response = OpenApiResponse(
    response=MessageSerializer,
    examples=[
        OpenApiExample(
            name='Authentication not provided',
            value=NO_AUTH,
            status_codes=['401']
        ),
        OpenApiExample(
            name='Invalid token',
            value=INVALID_TOKEN,
            status_codes=['401']
        )
    ]
)
auth_no_permissions_response = OpenApiResponse(
    response=MessageSerializer,
    examples=[
        OpenApiExample(
            name='Permission denied',
            value=PERMISSION_DENIED,
            status_codes=['403']
        )
    ]
)
invalid_user_list_response = OpenApiResponse(
    response=MessageSerializer,
    examples=[
        OpenApiExample(
            name='User List not found',
            value={'message': INVALID_USER_LIST},
            status_codes=[500]
        )
    ]
)
invalid_recipe_response = OpenApiResponse(
    response=MessageSerializer,
    examples=[
        OpenApiExample(
            name='Recipe not found',
            value={'message': INVALID_RECIPE},
            status_codes=[500]
        )
    ]
)
list_name_param = OpenApiParameter(
    name='list_name',
    description='Name of the list.',
    type=str,
    location=OpenApiParameter.PATH
)
custom_ingredient_name_param = OpenApiParameter(
    name='ingredient',
    description='Name of the custom ingredient.',
    type=str,
    location=OpenApiParameter.PATH
)
recipe_name_param = OpenApiParameter(
    name='recipe_name',
    description='Name of the recipe.',
    type=str,
    location=OpenApiParameter.PATH
)

def api_exception_handler(exc, context=None) -> Response:
    """
    API Exception handler.

    Args:
        exc: the request exception
        context: the exception context

    Returns:
        A json object with the error message
    """
    response = exception_handler(exc, context=context)
    if response and response.status_code == 403:
        response.data = PERMISSION_DENIED
    elif response and isinstance(response.data, dict):
        response.data = {'message': response.data.get('detail', 'API Error')}
    elif isinstance(exc, ValueError) or isinstance(exc, ObjectDoesNotExist):
        data = {'message': str(exc)}
        response = Response(data, status=500)
    else:
        data = {'message': 'API Error'}
        response = Response(data, status=500)
    return response


@extend_schema(tags=["User's List"])
class UpdateUserListIngredientsViewSet(viewsets.ViewSet):
    MISSING_ADD_INGREDIENT_MSG = (
        f'{REQUIRED_VALUE_MISSING}'
        '{list_name: [LISTNAME], ingredient: [INGREDIENT], '
        'amount: [AMOUNT/QUANTITY], unit: [MEASURMENT UNIT], '
        'is_custom_ingredient: [CUSTOM INGREDIENT BOOLEAN]}'
    )
    MISSING_SET_INGREDIENT_MSG = (
        f'{REQUIRED_VALUE_MISSING}'
        '{old_list_name: [LISTNAME], old_ingredient: [INGREDIENT], '
        'old_amount: [AMOUNT/QUANTITY], old_unit: [MEASURMENT UNIT], '
        'new_list_name: [LISTNAME], new_ingredient: [INGREDIENT], '
        'new_amount: [AMOUNT/QUANTITY], new_unit: [MEASURMENT UNIT] '
        'is_custom_ingredient: [CUSTOM INGREDIENT BOOLEAN]}'
    )
    MISSING_DELETE_INGREDIENT_MSG = (
        'Required query parameters missing from sent request. Please '
        'add the following query parameters'
        '?list_name=[LISTNAME]&ingredient=[INGREDIENT]'
        '&unit=[MEASURMENT UNIT]&is_custom_ingredient=[BOOLEAN]'
    )

    @extend_schema(
        request=inline_serializer(
            name='AddIngredientInListRequest',
            fields={
                'list_name': serializers.CharField(),
                'ingredient': serializers.CharField(),
                'amount': serializers.FloatField(),
                'unit': serializers.CharField(),
                'is_custom_ingredient': serializers.BooleanField()
            }
        ),
        responses={
            200: UserListIngredientsSerializer,
            400: MessageSerializer,
            401: auth_failed_response,
            500: invalid_user_list_response
        },
        examples=[
            OpenApiExample(
                name='Add Ingredient in List',
                value={
                    'list_name': 'Grocery',
                    'ingredient': 'Beef',
                    'amount': 500,
                    'unit': 'g',
                    'is_custom_ingredient': False
                },
                request_only=True
            ),
            OpenApiExample(
                name='Add Custom Ingredient in List',
                value={
                    'list_name': 'Grocery',
                    'ingredient': 'Homemade Meatball',
                    'amount': 25,
                    'unit': 'count',
                    'is_custom_ingredient': True
                },
                request_only=True
            ),
            OpenApiExample(
                name='Ingredient Added',
                value=GROCERY_LIST,
                status_codes=[200],
                response_only=True
            ),
            OpenApiExample(
                name='Required Value Missing',
                value={'message': MISSING_ADD_INGREDIENT_MSG},
                status_codes=[400],
                response_only=True
            )
        ]
    )
    def create(self, request: Request) -> Response:
        """
        Adds an ingredient to a specified user's list.
        """
        # Extract username from the access token
        username = get_auth_username_from_payload(request=request)
        body = request.data

        if (
            username
            and body.get('list_name', None)
            and body.get('ingredient', None)
            and body.get('amount', None)
            and body.get('unit', None)
            and body.get('is_custom_ingredient', None) is not None
        ):
            # Adding ingredient to a list
            list = add_list_ingredient(
                username=username,
                list_name=body['list_name'],
                ingredient=body['ingredient'],
                amount=body['amount'],
                unit=body['unit'],
                is_custom_ingredient=body['is_custom_ingredient']
            )
            serializer = UserListIngredientsSerializer(list)
        else:
            raise MissingInformation(self.MISSING_ADD_INGREDIENT_MSG)

        return Response(serializer.data, status=200)

    @extend_schema(
        request=inline_serializer(
            name='UpdateIngredientInListRequest',
            fields={
                'old_list_name': serializers.CharField(),
                'old_ingredient': serializers.CharField(),
                'old_amount': serializers.FloatField(),
                'old_unit': serializers.CharField(),
                'old_is_custom_ingredient': serializers.BooleanField(),
                'new_list_name': serializers.CharField(),
                'new_ingredient': serializers.CharField(),
                'new_amount': serializers.FloatField(),
                'new_unit': serializers.CharField(),
                'new_is_custom_ingredient': serializers.BooleanField()
            }
        ),
        responses={
            200: UserListIngredientsSerializer(many=True),
            400: MessageSerializer,
            401: auth_failed_response,
            500: invalid_user_list_response
        },
        examples=[
            OpenApiExample(
                name='Update Ingredient in same List',
                value={
                    'old_list_name': 'Grocery',
                    'old_ingredient': 'Beef',
                    'old_amount': 400,
                    'old_unit': 'lb',
                    'old_is_custom_ingredient': False,
                    'new_list_name': 'Grocery',
                    'new_ingredient': 'Beef',
                    'new_amount': 500,
                    'new_unit': 'g',
                    'new_is_custom_ingredient': False
                },
                request_only=True
            ),
            OpenApiExample(
                name='Move Ingredient in List to Another List',
                value={
                    'old_list_name': 'Grocery',
                    'old_ingredient': 'Pork',
                    'old_amount': 500,
                    'old_unit': 'g',
                    'old_is_custom_ingredient': False,
                    'new_list_name': 'Pantry',
                    'new_ingredient': 'Pork',
                    'new_amount': 500,
                    'new_unit': 'g',
                    'new_is_custom_ingredient': False
                },
                request_only=True
            ),
            OpenApiExample(
                name='Ingredient Updated',
                value=GROCERY_LIST,
                status_codes=[200],
                response_only=True
            ),
            OpenApiExample(
                name='Required Value Missing',
                value={'message': MISSING_SET_INGREDIENT_MSG},
                status_codes=[400],
                response_only=True
            )
        ]
    )
    def update(self, request: Request) -> Response:
        """
        Sets or moves an ingredient in a specified user's list.
        Subtracts the old ingredient amount from the specified "old" list and
        adds the new ingredient amount to the specified "new" list.
        Returns all of the user's lists.
        """
        # Extract username from the access token
        username = get_auth_username_from_payload(request=request)
        body = request.data

        if (
            username
            and body.get('old_list_name', None)
            and body.get('old_ingredient', None)
            and body.get('old_amount', -1) >= 0
            and body.get('old_unit', None)
            and body.get('old_is_custom_ingredient', None) is not None
            and body.get('new_list_name', None)
            and body.get('new_ingredient', None)
            and body.get('new_amount', None)
            and body.get('new_unit', None)
            and body.get('new_is_custom_ingredient', None) is not None
        ):
            updated_lists = set_list_ingredient(
                username=username,
                old_list_name=body['old_list_name'],
                old_ingredient=body['old_ingredient'],
                old_amount=body['old_amount'],
                old_unit=body['old_unit'],
                old_is_custom_ingredient=body['old_is_custom_ingredient'],
                new_list_name=body['new_list_name'],
                new_ingredient=body['new_ingredient'],
                new_amount=body['new_amount'],
                new_unit=body['new_unit'],
                new_is_custom_ingredient=body['new_is_custom_ingredient'],
            )

            serializer = UserListIngredientsSerializer(updated_lists, many=True)
        else:
            raise MissingInformation(self.MISSING_SET_INGREDIENT_MSG)

        return Response(serializer.data, status=200)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='list_name',
                description='Name of the list.',
                type=str,
                location=OpenApiParameter.QUERY,
                required=True
            ),
            OpenApiParameter(
                name='ingredient',
                description='Name of the ingredient.',
                type=str,
                location=OpenApiParameter.QUERY,
                required=True
            ),
            OpenApiParameter(
                name='unit',
                description='Unit of measurement for the ingredient.',
                type=str,
                location=OpenApiParameter.QUERY,
                required=True
            ),
            OpenApiParameter(
                name='is_custom_ingredient',
                description='Flag if ingredient is a custom ingredient or not.',
                type=bool,
                location=OpenApiParameter.QUERY,
                required=True
            )
        ],
        request=None,
        responses={
            200: UserListIngredientsSerializer,
            400: MessageSerializer,
            401: auth_failed_response,
            500: invalid_user_list_response
        },
        examples=[
            OpenApiExample(
                name='Ingredient Deleted',
                value=GROCERY_LIST,
                status_codes=[200],
                response_only=True
            ),
            OpenApiExample(
                name='Required Value Missing',
                value={'message': MISSING_DELETE_INGREDIENT_MSG},
                status_codes=[400],
                response_only=True
            ),
        ]
    )
    def destroy(self, request: Request) -> Response:
        """
        Deletes an ingredient from a specified user's list.
        """
        # Extract username from the access token
        username = get_auth_username_from_payload(request=request)
        query_params = request.query_params

        if (
            username
            and query_params.get('list_name', None)
            and query_params.get('ingredient', None)
            and query_params.get('unit', None)
            and query_params.get('is_custom_ingredient', None) is not None
        ):
            list = delete_list_ingredient(
                username=username,
                list_name=query_params['list_name'],
                ingredient=query_params['ingredient'],
                unit=query_params['unit'],
                is_custom_ingredient=query_params['is_custom_ingredient']
            )
            serializer = UserListIngredientsSerializer(list)
        else:
            raise MissingInformation(self.MISSING_DELETE_INGREDIENT_MSG)

        return Response(serializer.data, status=200)


@extend_schema(tags=["User's List"])
class UserListIngredientsViewSet(viewsets.ViewSet):
    MISSING_USER_LIST_PARAM_MSG = 'list_name parameter is missing or empty.'
    MISSING_UPDATE_INGREDIENT_MSG = (
        f'{REQUIRED_VALUE_MISSING}'
        '{old_list_name: [LISTNAME], new_list_name: [LISTNAME]}'
    )

    @extend_schema(
        request=None,
        responses={
            200: UserListIngredientsSerializer(many=True),
            401: auth_failed_response,
        },
        examples=[
            OpenApiExample(
                name="All User Lists Retrieved",
                value=GROCERY_LIST,
                status_codes=[200]
            )
        ]
    )
    def list(self, request: Request) -> Response:
        """
        Retrieves all the lists for a user.
        """
        username = get_auth_username_from_payload(request=request)

        # Retrieves all the lists for the user
        lists = get_user_lists_ingredients(username=username)
        serializer = UserListIngredientsSerializer(lists, many=True)

        return Response(serializer.data, status=200)

    @extend_schema(
        parameters=[list_name_param],
        request=None,
        responses={
            201: UserListIngredientsSerializer,
            400: MessageSerializer,
            401: auth_failed_response,
            500: MessageSerializer
        },
        examples=[
            OpenApiExample(
                name="User's List Created",
                value={
                    'user': 'teacup',
                    'list_name': 'Grocery',
                    'ingredients': []
                },
                status_codes=[201]
            ),
            OpenApiExample(
                name='Required Value Missing',
                value={'message': MISSING_USER_LIST_PARAM_MSG},
                status_codes=[400]
            ),
            OpenApiExample(
                name='Max User Lists Reached',
                value={'message': MAX_LISTS_PER_USER},
                status_codes=[500]
            )
        ]
    )
    def create(self, request: Request, list_name: str = None) -> Response:
        """
        Create a new list for the user in the database. Users are limited to
        10 lists per user.
        """
        # Extract username from the access token
        username = get_auth_username_from_payload(request=request)

        if username and list_name:
            # Check listName object exists, if not add
            create_list_name(list_name=list_name)

            # Create the list
            list = create_user_list_ingredients(
                username,
                list_name
            )
            serializer = UserListIngredientsSerializer(list)
        else:
            raise MissingInformation(self.MISSING_USER_LIST_PARAM_MSG)

        return Response(serializer.data, status=201)

    @extend_schema(
        parameters=[list_name_param],
        request=None,
        responses={
            200: UserListIngredientsSerializer,
            401: auth_failed_response,
            500: invalid_user_list_response
        },
        examples=[
            OpenApiExample(
                name="User List Retrieved",
                value=GROCERY_LIST,
                status_codes=[200]
            )
        ]
    )
    def retrieve(self, request: Request, list_name: str = None) -> Response:
        """
        Retrieves the specific list for a user.
        """
        username = get_auth_username_from_payload(request=request)

        # Retrieves the specific list for the user
        my_list = get_specific_user_lists_ingredients(
            username=username,
            list_name=list_name
        )
        serializer = UserListIngredientsSerializer(my_list)

        return Response(serializer.data, status=200)

    @extend_schema(
        request=inline_serializer(
            name='ChangeUserIngredientsListNameRequest',
            fields={
                'old_list_name': serializers.CharField(),
                'new_list_name': serializers.CharField()
            }
        ),
        responses={
            200: UserListIngredientsSerializer,
            400: MessageSerializer,
            401: auth_failed_response,
            500: invalid_user_list_response
        },
        examples=[
            OpenApiExample(
                name='Change List Name',
                value={'old_list_name': 'Pantry', 'new_list_name': 'Fridge'},
                request_only=True
            ),
            OpenApiExample(
                name='List Name Changed',
                value=FRIDGE_LIST,
                status_codes=[200],
                response_only=True
            ),
            OpenApiExample(
                name='Required Value Missing',
                value={'message': MISSING_UPDATE_INGREDIENT_MSG},
                status_codes=[400],
                response_only=True
            )
        ]
    )
    def update(self, request: Request) -> Response:
        """
        Changes the specified user's list name to another name.
        """
        # Extract username from the access token
        username = get_auth_username_from_payload(request=request)
        body = request.data

        if (
            username
            and body.get('old_list_name', None)
            and body.get('new_list_name', None)
        ):
            list = change_user_list_ingredient_name(
                username=username,
                old_list_name=body['old_list_name'],
                new_list_name=body['new_list_name']
            )
            serializer = UserListIngredientsSerializer(list)
        else:
            raise MissingInformation(self.MISSING_UPDATE_INGREDIENT_MSG)

        return Response(serializer.data, status=200)

    @extend_schema(
        parameters=[list_name_param],
        request=None,
        responses={
            200: UserListIngredientsSerializer(many=True),
            401: auth_failed_response
        },
        examples=[
            OpenApiExample(
                name='List Deleted',
                value=GROCERY_LIST,
                status_codes=[200]
            )
        ]
    )
    def destroy(self, request: Response, list_name: str = None) -> Response:
        """
        Deletes the specified list from the user's lists and returns
        all of the user's lists after the delete.
        """
        username = get_auth_username_from_payload(request=request)

        # Delete the list for specified user
        lists = delete_user_list_ingredients(
            username=username,
            list_name=list_name
        )
        serializer = UserListIngredientsSerializer(lists, many=True)

        return Response(serializer.data, status=200)


@extend_schema(tags=['Ingredients'])
class IngredientsViewSet(viewsets.ViewSet):
    @extend_schema(
        request=None,
        responses={
            200: inline_serializer(
                name='AllIngredientsSerializer',
                fields={
                    'common_ingredients': IngredientSerializer(many=True),
                    'custom_ingredients': CustomIngredientSerializer(many=True)
                }
            ),
            401: auth_failed_response
        },
        examples=[
            OpenApiExample(
                name='All Ingredients Returned',
                value={
                    'common_ingredients': [{'name': 'Beef', 'type': 'Meat'}],
                    'custom_ingredients': [{'user': 'teacup', 'name': 'Beef', 'type': 'Meat'}]
                },
                status_codes=[200]
            )
        ]
    )
    def list(self, request: Request) -> Response:
        """
        Returns a dictionary containing the list of common ingredients
        and the list of user's custom ingredients in the database.
        """
        username = get_auth_username_from_payload(request=request)

        common_ingredients = get_all_ingredients()
        custom_ingredients = get_all_custom_ingredients(username=username)
        common_ing_serializer = IngredientSerializer(common_ingredients, many=True)
        custom_ing_serializer = CustomIngredientSerializer(custom_ingredients, many=True)
        return Response(
            {
                'common_ingredients': common_ing_serializer.data,
                'custom_ingredients': custom_ing_serializer.data
            },
            status=200
        )


@extend_schema(tags=['Users'])
class UserViewSet(viewsets.ViewSet):
    MISSING_USER_INFO = 'Username or email missing. Unable to create new user.'

    @extend_schema(
        request=None,
        responses={
            201: UserSerializer,
            400: MessageSerializer,
            401: auth_failed_response
        },
        examples=[
            OpenApiExample(
                name='User Created',
                value={'username': 'teacup', 'email': 'teacup@domain.com'},
                status_codes=[201]
            ),
            OpenApiExample(
                name='Unable to Create User',
                value={'message': MISSING_USER_INFO},
                status_codes=[400]
            )
        ]
    )
    def create(self, request: Request) -> Response:
        """
        Creates a new user in the database based on Auth0 access token.
        Returns the user object.
        """
        # Extract username and email from the access token
        username = get_auth_username_from_payload(request=request)
        email = get_auth_email_from_payload(request=request)

        if email and username:
            # Create user in the db
            user = create_user(username=username, email=email)
            serializer = UserSerializer(user)

            # Create Pantry and Grocery lists
            add_default_user_lists(username=username)
        else:
            raise MissingInformation(self.MISSING_USER_INFO)

        return Response(serializer.data, status=201)


@extend_schema(tags=['Measurements'])
class MeasurementsViewSet(viewsets.ViewSet):
    @extend_schema(
        request=None,
        responses={
            200: MeasurementSerializer(many=True),
            401: auth_failed_response
        },
        examples=[
            OpenApiExample(
                name='All Measurements Returned',
                value={'unit': 'g'},
                status_codes=[200]
            )
        ]
    )
    def list(self, request: Request) -> Response:
        """
        Returns a list of all measurements in the database.
        """
        all_measurements = get_all_measurements()
        serializer = MeasurementSerializer(all_measurements, many=True)
        return Response(serializer.data, status=200)


@extend_schema(tags=['CustomIngredients'])
class CustomIngredientsViewSet(viewsets.ViewSet):
    MISSING_ING = 'Missing ingredient and type in message body.'

    @extend_schema(
        request=inline_serializer(
            name='AddCustomIngredientRequest',
            fields={
                'ingredient': serializers.CharField(),
                'type': serializers.CharField()
            }
        ),
        responses={
            201: CustomIngredientSerializer,
            400: MessageSerializer,
            401: auth_failed_response,
        },
        examples=[
            OpenApiExample(
                name='Custom Ingredient Created',
                value=SINGLE_CUSTOM_INGREDIENT_DICT,
                status_codes=[201],
                response_only=True
            ),
            OpenApiExample(
                name='Required Value Missing',
                value={'message': MISSING_ING},
                status_codes=[400],
                response_only=True
            )
        ]
    )
    def create(self, request: Request) -> Response:
        """
        Creates a custom ingredient for the user.
        Returns the custom ingredient object.
        """
        # Extract username from the access token
        username = get_auth_username_from_payload(request=request)
        body = request.data
        if (
            username
            and body.get('ingredient', None)
            and body.get('type', None)
        ):
            custom_ingredient = create_custom_ingredient(
                username=username,
                name=body['ingredient'],
                type=body['type']
            )
        else:
            raise MissingInformation(self.MISSING_ING)

        serializer = CustomIngredientSerializer(custom_ingredient)
        return Response(serializer.data, status=201)

    @extend_schema(
        parameters=[custom_ingredient_name_param],
        request=None,
        responses={
            200: CustomIngredientSerializer(many=True),
            401: auth_failed_response,
        },
        examples=[
            OpenApiExample(
                name='Custom Ingredient Deleted',
                value=SINGLE_CUSTOM_INGREDIENT_DICT,
                status_codes=[200]
            )
        ]
    )
    def destroy(self, request: Response, ingredient: str = None) -> Response:
        """
        Deletes a custom ingredient for the user.
        Returns the list of remaining custom ingredients for the user
        """
        # Extract username from the access token
        username = get_auth_username_from_payload(request=request)

        remaining_custom = delete_custom_ingredient(
            username=username,
            ingredient=ingredient
        )

        serializer = CustomIngredientSerializer(remaining_custom, many=True)
        return Response(serializer.data, status=200)


@extend_schema(tags=['Recipes'])
class UpdateRecipeIngredientsViewSet(viewsets.ViewSet):
    MISSING_RECIPE_PARAM_MSG = 'recipe_name parameter is missing or empty.'
    MISSING_ADD_INGREDIENT_MSG = (
        f'{REQUIRED_VALUE_MISSING}'
        '{list_name: [LISTNAME], ingredient: [INGREDIENT], '
        'amount: [AMOUNT/QUANTITY], unit: [MEASURMENT UNIT], '
        'is_custom_ingredient: [CUSTOM INGREDIENT BOOLEAN]}'
    )
    MISSING_DELETE_INGREDIENT_MSG = (
        'Required query parameters missing from sent request. Please '
        'add the following query parameters'
        '?list_name=[LISTNAME]&ingredient=[INGREDIENT]'
        '&unit=[MEASURMENT UNIT]&is_custom_ingredient=[BOOLEAN]'
    )
    @extend_schema(
        parameters=[recipe_name_param],
        request=inline_serializer(
            name='AddIngredientInRecipeRequest',
            fields={
                'ingredient': serializers.CharField(),
                'amount': serializers.FloatField(),
                'unit': serializers.CharField(),
                'is_custom_ingredient': serializers.BooleanField()
            }
        ),
        responses={
            200: RecipeSerializer,
            400: MessageSerializer,
            401: auth_failed_response,
            500: invalid_recipe_response
        },
        examples=[
            OpenApiExample(
                name='Add Ingredient in Recipe',
                value={
                    'ingredient': 'Bread',
                    'amount': 1,
                    'unit': 'count',
                    'is_custom_ingredient': False
                },
                request_only=True
            ),
            OpenApiExample(
                name='Add Custom Ingredient in Recipe',
                value={
                    'ingredient': 'Jam',
                    'amount': 25,
                    'unit': 'g',
                    'is_custom_ingredient': True
                },
                request_only=True
            ),
            OpenApiExample(
                name='Ingredient Added',
                value=SINGLE_RECIPE,
                status_codes=[200],
                response_only=True
            ),
            OpenApiExample(
                name='Required Value Missing',
                value={'message': MISSING_ADD_INGREDIENT_MSG},
                status_codes=[400],
                response_only=True
            )
        ]
    )
    def create(self, request: Response, recipe_name: str = None) -> Response:
        """
        Adds an ingredient to a specified user's recipe.
        """
        # Extract username from the access token
        username = get_auth_username_from_payload(request=request)
        body = request.data

        if (
            username
            and recipe_name
            and body.get('ingredient', None)
            and body.get('amount', None)
            and body.get('unit', None)
            and body.get('is_custom_ingredient', None) is not None
        ):
            # Adding ingredient to a list
            my_recipe = add_ingredient_to_recipe(
                username=username,
                recipe_name=recipe_name,
                ingredient=body['ingredient'],
                amount=body['amount'],
                unit=body['unit'],
                is_custom_ingredient=body['is_custom_ingredient']
            )
            serializer = RecipeSerializer(my_recipe)
        elif not recipe_name:
            raise MissingInformation(self.MISSING_RECIPE_PARAM_MSG)
        else:
            raise MissingInformation(self.MISSING_ADD_INGREDIENT_MSG)

        return Response(serializer.data, status=200)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='ingredient',
                description='Name of the ingredient.',
                type=str,
                location=OpenApiParameter.QUERY,
                required=True
            ),
            OpenApiParameter(
                name='unit',
                description='Unit of measurement for the ingredient.',
                type=str,
                location=OpenApiParameter.QUERY,
                required=True
            ),
            OpenApiParameter(
                name='is_custom_ingredient',
                description='Flag if ingredient is a custom ingredient or not.',
                type=bool,
                location=OpenApiParameter.QUERY,
                required=True
            )
        ],
        request=None,
        responses={
            200: RecipeSerializer,
            400: MessageSerializer,
            401: auth_failed_response,
            500: invalid_recipe_response
        },
        examples=[
            OpenApiExample(
                name='Ingredient Deleted',
                value=SINGLE_RECIPE,
                status_codes=[200],
                response_only=True
            ),
            OpenApiExample(
                name='Required Value Missing',
                value={'message': MISSING_DELETE_INGREDIENT_MSG},
                status_codes=[400],
                response_only=True
            ),
        ]
    )
    def destroy(self, request: Response, recipe_name: str = None) -> Response:
        """
        Deletes an ingredient from a specified user's recipe.
        """
        # Extract username from the access token
        username = get_auth_username_from_payload(request=request)
        body = request.data

        if (
            username
            and recipe_name
            and body.get('ingredient', None)
            and body.get('unit', None)
            and body.get('is_custom_ingredient', None) is not None
        ):
            my_recipe = delete_list_ingredient(
                username=username,
                recipe_name=recipe_name,
                ingredient=body['ingredient'],
                unit=body['unit'],
                is_custom_ingredient=body['is_custom_ingredient']
            )
            serializer = RecipeSerializer(my_recipe)
        elif not recipe_name:
            raise MissingInformation(self.MISSING_RECIPE_PARAM_MSG)
        else:
            raise MissingInformation(self.MISSING_DELETE_INGREDIENT_MSG)

        return Response(serializer.data, status=200)


@extend_schema(tags=['Recipes'])
class UpdateRecipeStepsViewSet(viewsets.ViewSet):
    MISSING_RECIPE_PARAM_MSG = 'recipe_name parameter is missing or empty.'
    MISSING_STEP_MSG = (
        'Required query parameters missing from sent request. Please '
        'add the following query parameters'
        '?recipe_name=[STRING]&step=[STRING]'
    )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='step_number',
                description='The number step to remove from a recipe.',
                type=str,
                location=OpenApiParameter.QUERY,
                required=True
            ),
        ],
        request=None,
        responses={
            200: RecipeSerializer,
            400: MessageSerializer,
            401: auth_failed_response,
            500: invalid_recipe_response
        },
        examples=[
            OpenApiExample(
                name='Step Deleted',
                value=SINGLE_RECIPE,
                status_codes=[200],
                response_only=True
            ),
            OpenApiExample(
                name='Required Value Missing',
                value={'message': MISSING_STEP_MSG},
                status_codes=[400],
                response_only=True
            ),
        ]
    )
    def destroy(self, request: Response, recipe_name: str = None) -> Response:
        """
        Deletes an step from a specified user's recipe.
        """
        # Extract username from the access token
        username = get_auth_username_from_payload(request=request)
        body = request.data

        if (
            username
            and recipe_name
            and body.get('step_number', None)
        ):
            recipe = remove_step_from_recipe(
                username=username,
                recipe_name=recipe_name,
                step_number=body['step']
            )
            serializer = RecipeSerializer(recipe)
        else:
            raise MissingInformation(self.MISSING_STEP_MSG)

        return Response(serializer.data, status=200)
    
    @extend_schema(
        parameters=[recipe_name_param],
        request=inline_serializer(
            name='AddStepInRecipeRequest',
            fields={
                'step': serializers.CharField(),
            }
        ),
        responses={
            200: RecipeSerializer,
            400: MessageSerializer,
            401: auth_failed_response,
            500: invalid_recipe_response
        },
        examples=[
            OpenApiExample(
                name='Add Step in Recipe',
                value={
                    'step': 'A step in my recipe!',
                },
                request_only=True
            ),
            OpenApiExample(
                name='Step Added',
                value=SINGLE_RECIPE,
                status_codes=[200],
                response_only=True
            ),
            OpenApiExample(
                name='Required Value Missing',
                value={'message': MISSING_STEP_MSG},
                status_codes=[400],
                response_only=True
            )
        ]
    )
    def create(self, request: Response, recipe_name: str = None) -> Response:
        """
        Adds an step to a specified user's recipe.
        """
        # Extract username from the access token
        username = get_auth_username_from_payload(request=request)
        body = request.data

        if (
            username
            and recipe_name
            and body.get('step', None)
        ):
            # Adding ingredient to a list
            my_recipe = add_step_to_recipe(
                username=username,
                recipe_name=recipe_name,
                step=body['step'],
            )
            serializer = RecipeSerializer(my_recipe)
        elif not recipe_name:
            raise MissingInformation(self.MISSING_RECIPE_PARAM_MSG)
        else:
            raise MissingInformation(self.MISSING_STEP_MSG)

        return Response(serializer.data, status=200)


    @extend_schema(
        parameters=[recipe_name_param],
        request=inline_serializer(
            name='UpdateStepInRecipeRequest',
            fields={
                'step': serializers.CharField(),
            }
        ),
        responses={
            200: RecipeSerializer,
            400: MessageSerializer,
            401: auth_failed_response,
            500: invalid_recipe_response
        },
        examples=[
            OpenApiExample(
                name='New step in Recipe',
                value={
                    'step': 'A step in my recipe!'
                },
                request_only=True
            ),
            OpenApiExample(
                name='The number step to update from a recipe',
                value={
                    'step_number': 1
                },
                request_only=True
            ),
            OpenApiExample(
                name='Step Updated',
                value=SINGLE_RECIPE,
                status_codes=[200],
                response_only=True
            ),
            OpenApiExample(
                name='Required Value Missing',
                value={'message': MISSING_STEP_MSG},
                status_codes=[400],
                response_only=True
            )
        ]
    )
    def update(self, request: Response, recipe_name: str = None) -> Response:
        """
        Updates a step in a specified user's recipe.
        """
        # Extract username from the access token
        username = get_auth_username_from_payload(request=request)
        body = request.data

        if (
            username
            and recipe_name
            and body.get('step', None)
            and body.get('step_number', None)
        ):
            # Adding ingredient to a list
            my_recipe = edit_step_in_recipe(
                username=username,
                recipe_name=recipe_name,
                new_step=body['step'],
                step_number=body['step_number'],
            )
            serializer = RecipeSerializer(my_recipe)
        elif not recipe_name:
            raise MissingInformation(self.MISSING_RECIPE_PARAM_MSG)
        else:
            raise MissingInformation(self.MISSING_STEP_MSG)

        return Response(serializer.data, status=200)


@extend_schema(tags=['Recipes'])
class RecipeViewSet(viewsets.ViewSet):
    MISSING_USER_LIST_PARAM_MSG = 'recipe_name parameter is missing or empty.'

    @extend_schema(
        request=None,
        responses={
            200: RecipeSerializer(many=True),
            401: auth_failed_response,
        },
        examples=[
            OpenApiExample(
                name="All User Lists Retrieved",
                value=[SINGLE_RECIPE],
                status_codes=[200]
            )
        ]
    )
    def list(self, request: Request) -> Response:
        """
        Retrieves all the recipes for a user.
        """
        username = get_auth_username_from_payload(request=request)
        print(username)
        # Retrieves all the lists for the user
        recipes = get_all_recipes(username=username)
        serializer = RecipeSerializer(recipes, many=True)

        return Response(serializer.data, status=200)

    @extend_schema(
        parameters=[recipe_name_param],
        request=None,
        responses={
            201: RecipeSerializer,
            400: MessageSerializer,
            401: auth_failed_response,
        },
        examples=[
            OpenApiExample(
                name="Recipe Created",
                value={
                    'user': 'teacup',
                    'recipe_name': 'Toast',
                    'ingredients': [],
                    'steps':[]
                },
                status_codes=[201]
            ),
            OpenApiExample(
                name='Required Value Missing',
                value={'message': MISSING_USER_LIST_PARAM_MSG},
                status_codes=[400]
            )
        ]
    )
    def create(self, request: Response, recipe_name: str = None) -> Response:
        """
        Creates a recipe for the user.
        Returns the recipe object.
        """
        # Extract username from the access token
        username = get_auth_username_from_payload(request=request)
        if username and recipe_name:
            # Create the list
            my_recipe = create_recipe(
                username=username,
                recipe_name=recipe_name
            )
            serializer = RecipeSerializer(my_recipe)
        else:
            raise MissingInformation(self.MISSING_USER_LIST_PARAM_MSG)

        return Response(serializer.data, status=201)
    
    @extend_schema(
        parameters=[recipe_name_param],
        request=None,
        responses={
            200: RecipeSerializer,
            401: auth_failed_response,
            500: invalid_recipe_response
        },
        examples=[
            OpenApiExample(
                name="Recipe Retrieved",
                value=SINGLE_RECIPE,
                status_codes=[200]
            )
        ]
    )
    def retrieve(self, request: Response, recipe_name: str = None) -> Response:
        """
        Retrieves the specific recipe for a user.
        """
       
        username = get_auth_username_from_payload(request=request)
        print(username)
        print(recipe_name)
        # Retrieves the specific list for the user
        my_recipe = get_recipe(
            username=username,
            recipe_name=recipe_name
        )
        serializer = RecipeSerializer(my_recipe)

        return Response(serializer.data, status=200)
    
    @extend_schema(
        parameters=[recipe_name_param],
        request=None,
        responses={
            200: RecipeSerializer(many=True),
            401: auth_failed_response
        },
        examples=[
            OpenApiExample(
                name='Recipe Deleted',
                value=[SINGLE_RECIPE],
                status_codes=[200]
            )
        ]
    )
    def destroy(self, request: Response, recipe_name: str = None) -> Response:
        """
        Deletes the specified recipe from the user's recipes and returns
        all of the user's recipes after the delete.
        """
        username = get_auth_username_from_payload(request=request)
        print(username)
        print(recipe_name)
        # Delete the list for specified user
        recipes = delete_recipe(
            username=username,
            recipe_name=recipe_name
        )
        serializer = RecipeSerializer(recipes, many=True)

        return Response(serializer.data, status=200)
    