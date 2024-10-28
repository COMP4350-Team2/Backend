from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import (
    extend_schema,
    inline_serializer,
    OpenApiExample,
    OpenApiResponse
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
    create_user,
    create_list_name,
    create_user_list_ingredients,
    delete_user_list_ingredients,
    get_all_ingredients,
    get_user_lists_ingredients,
    get_specific_user_lists_ingredients,
    update_list_ingredient,
    DOES_NOT_EXIST,
    INVALID_USER_LIST
)
from cupboard_app.serializers import (
    MessageSerializer,
    IngredientSerializer,
    UserSerializer,
    UserListIngredientsSerializer,
    UserListIngredientsViewSerializer
)

NO_AUTH = {'message': 'Authentication credentials were not provided.'}
INVALID_TOKEN = {'message': 'Given token not valid for any token type'}
PERMISSION_DENIED = {
    'message': 'Permission denied. You do not have permission to perform this action.'
}

GROCERY_LIST = {
    'user': 'teacup',
    'list_name': 'Grocery',
    'ingredients': [
        {
            "ingredient_id": 1,
            "ingredient_name": 'Beef',
            "amount": 500,
            "unit_id": 1,
            "unit": 'g'
        },
        {
            "ingredient_id": 1,
            "ingredient_name": 'Dairy',
            "amount": 2,
            "unit_id": 2,
            "unit": 'L'
        }
    ]
}
PANTRY_LIST = {
    'user': 'teacup',
    'list_name': 'Pantry',
    'ingredients': [
        {
            "ingredient_id": 1,
            "ingredient_name": 'Beef',
            "amount": 500,
            "unit_id": 1,
            "unit": 'g'
        },
        {
            "ingredient_id": 1,
            "ingredient_name": 'Dairy',
            "amount": 2,
            "unit_id": 2,
            "unit": 'L'
        }
    ]
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
        print(exc)
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
class UserListIngredientsViewSet(viewsets.ViewSet):
    MISSING_USER_LIST_PARAM_MSG = 'list_name parameter missing.'
    MISSING_UPDATE_INGREDIENT_MSG = (
        'Required value missing from sent request, '
        'please ensure all items are sent in the following format: '
        '{list_name: [LISTNAME], ingredient: [INGREDIENT], '
        'amount: [AMOUNT/QUANTITY], unit: [MEASURMENT UNIT], action: [ADD or DELETE]}'
    )

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(
                response=UserListIngredientsSerializer,
                examples=[
                    OpenApiExample(
                        name="User's List Created",
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
        Create a new list for a user in the database.
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
                        name="User's List Created",
                        value=GROCERY_LIST,
                        status_codes=[200]
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
    def retrieve(self, request: Request, list_name: str = None) -> Response:
        """
        Retrieves the specific list for a user.
        """
        username = get_auth_username_from_payload(request=request)
        # Retrieves the specific list for the user
        if username and list_name:
            my_list = get_specific_user_lists_ingredients(
                username=username,
                list_name=list_name
            )
            serializer = UserListIngredientsSerializer(my_list)
        else:
            MissingInformation(self.MISSING_USER_LIST_PARAM_MSG)

        return Response({'result': serializer.data}, status=200)

    @extend_schema(
        request=UserListIngredientsViewSerializer,
        responses={
            200: OpenApiResponse(
                response=UserListIngredientsSerializer,
                examples=[
                    OpenApiExample(
                        name='Item Updated',
                        value=GROCERY_LIST,
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
            500: OpenApiResponse(
                response=MessageSerializer,
                examples=[
                    OpenApiExample(
                        name='User List not found',
                        value={'message': INVALID_USER_LIST},
                        status_codes=[500]
                    ),
                    OpenApiExample(
                        name='Ingredient not found',
                        value={'message': f'Ingredient {DOES_NOT_EXIST}'},
                        status_codes=[500]
                    ),
                    OpenApiExample(
                        name='Unit not found',
                        value={'message': f'Measurement {DOES_NOT_EXIST}'},
                        status_codes=[500]
                    ),
                ]
            )
        }
    )
    def update(self, request: Request) -> Response:
        """
        Updates the ingredients for a user's list. Either adds or subtracts
        an ingredient in the user's list.
        """
        # Extract username from the access token
        username = get_auth_username_from_payload(request=request)
        body = request.data

        if (
            username
            and 'list_name' in body
            and 'ingredient' in body
            and 'amount' in body
            and 'unit' in body
            and 'action' in body
        ):
            list = update_list_ingredient(
                username,
                body['list_name'],
                body['ingredient'],
                body['amount'],
                body['unit'],
                body['action']
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
                    name='AllIngredientsResponse',
                    fields={
                        'result': UserListIngredientsSerializer(many=True),
                    }
                ),
                examples=[
                    OpenApiExample(
                        name='Success',
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
        Deletes a user's list.
        """
        username = get_auth_username_from_payload(request=request)

        if username and list_name:
            # Delete the list for specified user
            lists = delete_user_list_ingredients(
                username=username,
                list_name=list_name
            )
            serializer = UserListIngredientsSerializer(lists, many=True)
        else:
            raise MissingInformation(self.MISSING_USER_LIST_PARAM_MSG)

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
                        name='Success',
                        value={
                            'result': [
                                {
                                    'name': 'ingredient_1',
                                    'type': 'ingredient_type'
                                },
                                {
                                    'name': 'ingredient_2',
                                    'type': 'ingredint_type2'
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
                        name='Unable to create user',
                        value={'message': MISSING_USER_INFO},
                        status_codes=[400]
                    )
                ]
            ),
            401: auth_failed_response,
        }
    )
    def create(self, request: Request) -> Response:
        """
        Create a new user in the database based on Auth0 access token.
        """
        # Extract username and email from the access token
        username = get_auth_username_from_payload(request=request)
        email = get_auth_email_from_payload(request=request)

        if email and username:
            # Create user in the db
            user = create_user(username=username, email=email)
            serializer = UserSerializer(user)
        else:
            raise MissingInformation(self.MISSING_USER_INFO)

        return Response(serializer.data, status=201)
