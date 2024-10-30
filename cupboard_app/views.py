from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import (
    extend_schema,
    inline_serializer,
    OpenApiExample,
    OpenApiResponse,
    OpenApiRequest
)
from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import viewsets
from rest_framework.views import APIView, exception_handler

from utils.api_helper import (
    get_auth_username_from_payload,
    get_auth_email_from_payload
)
from utils.permissions import HasMessagesPermission
from cupboard_app.exceptions import MissingInformation
from cupboard_app.models import Message
from cupboard_app.queries import (
    add_default_user_lists,
    create_user,
    create_list_name,
    create_user_list_ingredients,
    delete_user_list_ingredients,
    get_all_ingredients,
    get_user_lists_ingredients,
    get_specific_user_lists_ingredients,
    add_list_ingredient,
    delete_list_ingredient,
    set_list_ingredient,
    change_user_list_ingredient_name,
    INVALID_USER_LIST
)
from cupboard_app.serializers import (
    MessageSerializer,
    IngredientSerializer,
    UserSerializer,
    UserListIngredientsSerializer
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
        'amount': 500,
        'unit_id': 1,
        'unit': 'g'
    },
    {
        'ingredient_id': 1,
        'ingredient_name': 'Dairy',
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
PANTRY_LIST = {
    'user': 'teacup',
    'list_name': 'Pantry',
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


@extend_schema(tags=['Messages'])
class PublicMessageAPIView(APIView):
    permission_classes = [AllowAny]
    text = "Hello from a public endpoint! You don't need to be authenticated to see this."

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(
                response=MessageSerializer,
                examples=[
                    OpenApiExample(
                        name='Success',
                        value={'message': text},
                        status_codes=[200]
                    )
                ]
            )
        }
    )
    def get(self, request: Request) -> Response:
        """
        This is an example of a public message API request.
        """
        message = Message(message=self.text)
        serializer = MessageSerializer(message)
        return Response(serializer.data)


@extend_schema(tags=['Messages'])
class PrivateMessageAPIView(APIView):
    text = 'Hello from a private endpoint! You need to be authenticated to see this.'

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(
                response=MessageSerializer,
                examples=[
                    OpenApiExample(
                        name='Success',
                        value={'message': text},
                        status_codes=[200]
                    )
                ]
            ),
            401: auth_failed_response
        }
    )
    def get(self, request: Request) -> Response:
        """
        This is an example of a private message API request.
        A valid access token is required to access this route.
        """
        message = Message(message=self.text)
        serializer = MessageSerializer(message)
        return Response(serializer.data)


@extend_schema(tags=['Messages'])
class PrivateScopedMessageAPIView(APIView):
    permission_classes = [HasMessagesPermission]
    text = (
        'Hello from a private endpoint! You need to be authenticated '
        'and have a permission of read:messages to see this.'
    )

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(
                response=MessageSerializer,
                examples=[
                    OpenApiExample(
                        name='Success',
                        value={'message': text},
                        status_codes=[200]
                    )
                ]
            ),
            401: auth_failed_response,
            403: auth_no_permissions_response
        }
    )
    def get(self, request: Request) -> Response:
        """
        This is an example of a private scoped message API request.
        A valid access token and an appropriate permissions
        are required to access this route.
        """
        message = Message(message=self.text)
        serializer = MessageSerializer(message)
        return Response(serializer.data)


@extend_schema(tags=["User's List"])
class ListIngredientViewSet(viewsets.ViewSet):
    MISSING_ADD_INGREDIENT_MSG = (
        REQUIRED_VALUE_MISSING,
        '{list_name: [LISTNAME], ingredient: [INGREDIENT], '
        'amount: [AMOUNT/QUANTITY], unit: [MEASURMENT UNIT]}'
    )
    MISSING_DELETE_INGREDIENT_MSG = (
        REQUIRED_VALUE_MISSING,
        '{list_name: [LISTNAME], ingredient: [INGREDIENT], unit: [MEASURMENT UNIT]}'
    )
    MISSING_SET_INGREDIENT_MSG = (
        REQUIRED_VALUE_MISSING,
        '{list_name: [LISTNAME], old_ingredient: [INGREDIENT], '
        'old_unit: [MEASURMENT UNIT], new_ingredient: [INGREDIENT], '
        'new_amount: [AMOUNT/QUANTITY], new_unit: [MEASURMENT UNIT]}'
    )

    @extend_schema(
        request={
            'Add Ingredient in List': OpenApiRequest(
                request=inline_serializer(
                    name='AddIngredientInListRequest',
                    fields={
                        'list_name': serializers.CharField(),
                        'ingredient': serializers.CharField(),
                        'amount': serializers.FloatField(),
                        'unit': serializers.CharField()
                    }
                ),
                examples=[
                    OpenApiExample(
                        name='Add Ingredient in List',
                        value={
                            'list_name': 'Pantry',
                            'ingredient': 'Beef',
                            'amount': 500,
                            'unit': 'g'
                        }
                    )
                ]
            )
        },
        responses={
            200: OpenApiResponse(
                response=UserListIngredientsSerializer,
                examples=[
                    OpenApiExample(
                        name='Ingredient Added',
                        value=PANTRY_LIST,
                        status_codes=[200]
                    )
                ]
            ),
            400: OpenApiResponse(
                response=MessageSerializer,
                examples=[
                    OpenApiExample(
                        name='Required Value Missing',
                        value={'message': MISSING_ADD_INGREDIENT_MSG},
                        status_codes=[400]
                    ),
                ]
            ),
            401: auth_failed_response,
            500: invalid_user_list_response
        }
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
                unit=body['unit'],
                setting=False
            )
            serializer = UserListIngredientsSerializer(list)
        else:
            raise MissingInformation(self.MISSING_ADD_INGREDIENT_MSG)

        return Response(serializer.data, status=200)

    @extend_schema(
        request={
            'Update Ingredient in List': OpenApiRequest(
                request=inline_serializer(
                    name='UpdateIngredientInListRequest',
                    fields={
                        'list_name': serializers.CharField(),
                        'old_ingredient': serializers.CharField(),
                        'old_unit': serializers.CharField(),
                        'new_ingredient': serializers.CharField(),
                        'new_amount': serializers.FloatField(),
                        'new_unit': serializers.CharField()
                    }
                ),
                examples=[
                    OpenApiExample(
                        name='Update Ingredient in List',
                        value={
                            'list_name': 'Pantry',
                            'old_ingredient': 'Pork',
                            'old_unit': 'lb',
                            'new_ingredient': 'Beef',
                            'new_amount': 500,
                            'new_unit': 'g'
                        }
                    )
                ]
            )
        },
        responses={
            200: OpenApiResponse(
                response=UserListIngredientsSerializer,
                examples=[
                    OpenApiExample(
                        name='Ingredient Updated',
                        value=PANTRY_LIST,
                        status_codes=[200]
                    )
                ]
            ),
            400: OpenApiResponse(
                response=MessageSerializer,
                examples=[
                    OpenApiExample(
                        name='Required Value Missing',
                        value={'message': MISSING_SET_INGREDIENT_MSG},
                        status_codes=[400]
                    ),
                ]
            ),
            401: auth_failed_response,
            500: invalid_user_list_response
        }
    )
    def update(self, request: Request) -> Response:
        """
        Sets an ingredient in a specified user's list.
        """
        # Extract username from the access token
        username = get_auth_username_from_payload(request=request)
        body = request.data

        if (
            username
            and body.get('list_name', None)
            and body.get('old_ingredient', None)
            and body.get('old_unit', None)
            and body.get('new_ingredient', None)
            and body.get('new_amount', None)
            and body.get('new_unit', None)
        ):
            # Adding ingredient to a list
            list = set_list_ingredient(
                username=username,
                list_name=body['list_name'],
                old_ingredient=body['old_ingredient'],
                old_unit=body['old_unit'],
                new_ingredient=body['new_ingredient'],
                new_amount=body['new_amount'],
                new_unit=body['new_unit']
            )
            serializer = UserListIngredientsSerializer(list)
        else:
            raise MissingInformation(self.MISSING_SET_INGREDIENT_MSG)

        return Response(serializer.data, status=200)

    @extend_schema(
        request={
            'Delete Ingredient from List': OpenApiRequest(
                request=inline_serializer(
                    name='DeleteIngredientFromListRequest',
                    fields={
                        'list_name': serializers.CharField(),
                        'ingredient': serializers.CharField(),
                        'unit': serializers.CharField()
                    }
                ),
                examples=[
                    OpenApiExample(
                        name='Delete Ingredient from List',
                        value={
                            'list_name': 'Pantry',
                            'ingredient': 'Pork',
                            'unit': 'g'
                        }
                    )
                ]
            )
        },
        responses={
            200: OpenApiResponse(
                response=UserListIngredientsSerializer,
                examples=[
                    OpenApiExample(
                        name='Ingredient Deleted',
                        value=PANTRY_LIST,
                        status_codes=[200]
                    )
                ]
            ),
            400: OpenApiResponse(
                response=MessageSerializer,
                examples=[
                    OpenApiExample(
                        name='Required Value Missing',
                        value={'message': MISSING_DELETE_INGREDIENT_MSG},
                        status_codes=[400]
                    ),
                ]
            ),
            401: auth_failed_response,
            500: invalid_user_list_response
        }
    )
    def destroy(self, request: Request) -> Response:
        """
        Deletes an ingredient from a specified user's list.
        """
        # Extract username from the access token
        username = get_auth_username_from_payload(request=request)
        body = request.data

        if (
            username
            and body.get('list_name', None)
            and body.get('ingredient', None)
            and body.get('unit', None)
        ):
            list = delete_list_ingredient(
                username=username,
                list_name=body['list_name'],
                ingredient=body['ingredient'],
                unit=body['unit']
            )
            serializer = UserListIngredientsSerializer(list)
        else:
            raise MissingInformation(self.MISSING_DELETE_INGREDIENT_MSG)

        return Response(serializer.data, status=200)


@extend_schema(tags=["User's List"])
class UserListIngredientsViewSet(viewsets.ViewSet):
    MISSING_USER_LIST_PARAM_MSG = 'list_name parameter is missing or empty.'
    MISSING_UPDATE_INGREDIENT_MSG = (
        REQUIRED_VALUE_MISSING,
        '{old_list_name: [LISTNAME], new_list_name: [LISTNAME]}'
    )

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    name='AllUserIngredientsListsResponse',
                    fields={
                        'result': UserListIngredientsSerializer(many=True)
                    }
                ),
                examples=[
                    OpenApiExample(
                        name="All User Lists Retrieved",
                        value={
                            'result': [
                                GROCERY_LIST,
                                PANTRY_LIST
                            ]
                        },
                        status_codes=[200]
                    )
                ]
            ),
            401: auth_failed_response,
        }
    )
    def list(self, request: Request) -> Response:
        """
        Retrieves all the lists for a user.
        """
        username = get_auth_username_from_payload(request=request)

        # Retrieves all the lists for the user
        lists = get_user_lists_ingredients(username=username)
        serializer = UserListIngredientsSerializer(lists, many=True)

        return Response({'result': serializer.data}, status=200)

    @extend_schema(
        request=None,
        responses={
            201: OpenApiResponse(
                response=UserListIngredientsSerializer,
                examples=[
                    OpenApiExample(
                        name="User's List Created",
                        value={
                            'user': 'teacup',
                            'list_name': 'Grocery',
                            'ingredients': []
                        },
                        status_codes=[201]
                    )
                ]
            ),
            400: OpenApiResponse(
                response=MessageSerializer,
                examples=[
                    OpenApiExample(
                        name='Required Value Missing',
                        value={'message': MISSING_USER_LIST_PARAM_MSG},
                        status_codes=[400]
                    ),
                ]
            ),
            401: auth_failed_response,
        }
    )
    def create(self, request: Request, list_name: str = None) -> Response:
        """
        Create a new list for the user in the database.
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
        request=None,
        responses={
            200: OpenApiResponse(
                response=UserListIngredientsSerializer,
                examples=[
                    OpenApiExample(
                        name="User List Retrieved",
                        value=GROCERY_LIST,
                        status_codes=[200]
                    )
                ]
            ),
            401: auth_failed_response,
            500: invalid_user_list_response
        }
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
        request={
            'Change List Name': OpenApiRequest(
                request=inline_serializer(
                    name='ChangeUserIngredientsListNameRequest',
                    fields={
                        'old_list_name': serializers.CharField(),
                        'new_list_name': serializers.CharField()
                    }
                ),
                examples=[
                    OpenApiExample(
                        name='Change List Name',
                        value={
                            'old_list_name': 'Pantry',
                            'new_list_name': 'Fridge'
                        }
                    )
                ]
            )
        },
        responses={
            200: OpenApiResponse(
                response=UserListIngredientsSerializer,
                examples=[
                    OpenApiExample(
                        name='List Name Changed',
                        value=FRIDGE_LIST,
                        status_codes=[200]
                    )
                ]
            ),
            400: OpenApiResponse(
                response=MessageSerializer,
                examples=[
                    OpenApiExample(
                        name='Required Value Missing',
                        value={'message': MISSING_UPDATE_INGREDIENT_MSG},
                        status_codes=[400]
                    ),
                ]
            ),
            401: auth_failed_response,
            500: invalid_user_list_response
        }
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
        request=None,
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    name='AllUserIngredientsListsResponse',
                    fields={
                        'result': UserListIngredientsSerializer(many=True)
                    }
                ),
                examples=[
                    OpenApiExample(
                        name='List Deleted',
                        value={
                            'result': [
                                GROCERY_LIST,
                                PANTRY_LIST
                            ]
                        }
                    )
                ]
            ),
            401: auth_failed_response
        }
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

        return Response({'result': serializer.data}, status=200)


@extend_schema(tags=['Ingredients'])
class IngredientsViewSet(viewsets.ViewSet):
    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(
                response=inline_serializer(
                    name='AllIngredientsResponse',
                    fields={
                        'result': IngredientSerializer(many=True),
                    }
                ),
                examples=[
                    OpenApiExample(
                        name='All Ingredients Returned',
                        value={
                            'result': [
                                {
                                    'name': 'Beef',
                                    'type': 'Meat'
                                },
                                {
                                    'name': '2% Milk',
                                    'type': 'Dairy'
                                }
                            ]
                        }
                    )
                ]
            ),
            401: auth_failed_response
        }
    )
    def list(self, request: Request) -> Response:
        """
        Returns a list of all ingredients in database.
        """
        all_ingredients = get_all_ingredients()
        serializer = IngredientSerializer(all_ingredients, many=True)
        return Response({'result': serializer.data})


@extend_schema(tags=['User'])
class UserViewSet(viewsets.ViewSet):
    MISSING_USER_INFO = 'Username or email missing. Unable to create new user.'

    @extend_schema(
        request=None,
        responses={
            201: OpenApiResponse(
                response=UserSerializer,
                examples=[
                    OpenApiExample(
                        name='User Created',
                        value={
                            'username': 'teacup',
                            'email': 'teacup@domain.com'
                        },
                        status_codes=[201]
                    ),
                ]
            ),
            400: OpenApiResponse(
                response=MessageSerializer,
                examples=[
                    OpenApiExample(
                        name='Unable to Create User',
                        value={'message': MISSING_USER_INFO},
                        status_codes=[400]
                    )
                ]
            ),
            401: auth_failed_response
        }
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
