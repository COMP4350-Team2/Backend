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
    get_all_measurements,
    get_user_lists_ingredients,
    get_specific_user_lists_ingredients,
    add_list_ingredient,
    delete_list_ingredient,
    set_list_ingredient,
    change_user_list_ingredient_name,
    INVALID_USER_LIST,
    MAX_LISTS_PER_USER
)
from cupboard_app.serializers import (
    MessageSerializer,
    IngredientSerializer,
    MeasurementSerializer,
    UserSerializer,
    UserListIngredientsSerializer,
    CustomIngredientSerializer
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
        'ingredient_id': 1,
        'ingredient_name': 'Beef',
        'ingredient_type': 'Meat',
        'amount': 500,
        'unit_id': 1,
        'unit': 'g'
    },
    {
        'ingredient_id': 1,
        'ingredient_name': '2% Milk',
        'ingredient_type': 'Dairy',
        'amount': 2,
        'unit_id': 2,
        'unit': 'L'
    }
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
list_name_param = OpenApiParameter(
    name='list_name',
    description='Name of the list.',
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
        'amount: [AMOUNT/QUANTITY], unit: [MEASURMENT UNIT]}'
    )
    MISSING_SET_INGREDIENT_MSG = (
        f'{REQUIRED_VALUE_MISSING}'
        '{old_list_name: [LISTNAME], old_ingredient: [INGREDIENT], '
        'old_amount: [AMOUNT/QUANTITY], old_unit: [MEASURMENT UNIT], '
        'new_list_name: [LISTNAME], new_ingredient: [INGREDIENT], '
        'new_amount: [AMOUNT/QUANTITY], new_unit: [MEASURMENT UNIT]}'
    )

    @extend_schema(
        request=inline_serializer(
            name='AddIngredientInListRequest',
            fields={
                'list_name': serializers.CharField(),
                'ingredient': serializers.CharField(),
                'amount': serializers.FloatField(),
                'unit': serializers.CharField()
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
                    'unit': 'g'
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
        ):
            # Adding ingredient to a list
            list = add_list_ingredient(
                username=username,
                list_name=body['list_name'],
                ingredient=body['ingredient'],
                amount=body['amount'],
                unit=body['unit']
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
                'new_list_name': serializers.CharField(),
                'new_ingredient': serializers.CharField(),
                'new_amount': serializers.FloatField(),
                'new_unit': serializers.CharField()
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
                    'new_list_name': 'Grocery',
                    'new_ingredient': 'Beef',
                    'new_amount': 500,
                    'new_unit': 'g'
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
                    'new_list_name': 'Pantry',
                    'new_ingredient': 'Pork',
                    'new_amount': 500,
                    'new_unit': 'g'
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
            and body.get('new_list_name', None)
            and body.get('new_ingredient', None)
            and body.get('new_amount', None)
            and body.get('new_unit', None)
        ):
            updated_lists = set_list_ingredient(
                username=username,
                old_list_name=body['old_list_name'],
                old_ingredient=body['old_ingredient'],
                old_amount=body['old_amount'],
                old_unit=body['old_unit'],
                new_list_name=body['new_list_name'],
                new_ingredient=body['new_ingredient'],
                new_amount=body['new_amount'],
                new_unit=body['new_unit']
            )

            serializer = UserListIngredientsSerializer(updated_lists, many=True)
        else:
            raise MissingInformation(self.MISSING_SET_INGREDIENT_MSG)

        return Response(serializer.data, status=200)

    @extend_schema(
        parameters=[
            list_name_param,
            OpenApiParameter(
                name='ingredient',
                description='Name of the ingredient.',
                type=str,
                location=OpenApiParameter.PATH
            ),
            OpenApiParameter(
                name='unit',
                description='Unit of measurement for the ingredient.',
                type=str,
                location=OpenApiParameter.PATH
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
            )
        ]
    )
    def destroy(
        self,
        request: Request,
        list_name: str = None,
        ingredient: str = None,
        unit: str = None
    ) -> Response:
        """
        Deletes an ingredient from a specified user's list.
        """
        # Extract username from the access token
        username = get_auth_username_from_payload(request=request)

        list = delete_list_ingredient(
            username=username,
            list_name=list_name,
            ingredient=ingredient,
            unit=unit
        )
        serializer = UserListIngredientsSerializer(list)

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
            200: IngredientSerializer(many=True),
            401: auth_failed_response
        },
        examples=[
            OpenApiExample(
                name='All Ingredients Returned',
                value={'name': 'Beef', 'type': 'Meat'},
                status_codes=[200]
            )
        ]
    )
    def list(self, request: Request) -> Response:
        """
        Returns a list of all ingredients in the database.
        """
        all_ingredients = get_all_ingredients()
        serializer = IngredientSerializer(all_ingredients, many=True)
        return Response(serializer.data)


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
        return Response(serializer.data)


@extend_schema(tags=['CustomIngredients'])
class CustomIngredientsViewSet(viewsets.ViewSet):
    MISSING_USER_INFO = 'User missing. Unable to create new custom ingredient.'
    @extend_schema(
        request=None,
        responses={
            200: CustomIngredientSerializer(many=True),
            401: auth_failed_response
        },
        examples=[
            OpenApiExample(
                name='Custom Ingredient Created.',
                value={'username': 'teacup', 'name': 'Beef', 'type': 'Meat'},
                status_codes=[200]
            ),
            OpenApiExample(
                name='Custom Ingredient Deleted.',
                value={'username': 'teacup', 'name': 'Beef', 'type': 'Meat'},
                status_codes=[200]
            ),
            OpenApiExample(
                name='Unable to Create Custom Ingredient',
                value={'message': MISSING_USER_INFO},
                status_codes=[400]
            ),
            OpenApiExample(
                name='Unable to Delete Custom Ingredient',
                value={'message': MISSING_USER_INFO},
                status_codes=[400]
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

        if username:
            custom_ingredient = create_custom_ingredient(
                username=username,
                ingredient=body['ingredient'],
                type=body['type']
            )
            serializer = CustomIngredientSerializer(custom_ingredient)
        else:
            raise MissingInformation(self.MISSING_USER_INFO)

        return Response(serializer.data, status=200)
    
    def destroy(self, request: Response) -> Response:
        """
        Deletes a custom ingredient for the user.
        Returns the list of remaining custom ingredients for the user
        """
        username = get_auth_username_from_payload(request=request)
        body = request.data

        if username:
            list = delete_custom_ingredient(
                username=username,
                ingredient=body['ingredient']
            )
            serializer = CustomIngredientSerializer(list)
        else:
            raise MissingInformation(self.MISSING_USER_INFO)

        return Response(serializer.data, status=200)