from drf_spectacular.utils import (
    extend_schema,
    inline_serializer,
    OpenApiExample,
    OpenApiResponse
)
from rest_framework.exceptions import APIException
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
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
    create_user_list_ingredients,
    get_all_ingredients,
    update_list_ingredient,    
    DOES_NOT_EXIST_MSG,
    UPDATE_SUCCESS_MSG,
    UPDATE_FAILED_MSG
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
class UserListIngredientsAPIView(APIView):
    MISSING_CREATE_USER_LIST_MSG = 'list_name missing in the body.'
    MISSING_ADD_INGREDIENT_MSG = (
        'Required value missing from sent request, '
        'please ensure all items are sent in the following format: '
        '{list_name: [LISTNAME], ingredient: [INGREDIENT], '
        'amount: [AMOUNT/QUANTITY], unit: [MEASURMENT UNIT]}'
    )

    @extend_schema(
        request=inline_serializer(
            name='AllIngredientsResponse',
            fields={
                'result': IngredientSerializer(many=True),
            }
        ),
        responses={
            200: OpenApiResponse(
                response=UserListIngredientsSerializer,
                examples=[
                    OpenApiExample(
                        name="User's List Created",
                        value={
                            'result': {
                                'user': 'test_user',
                                'list_name': 'test_list',
                                'ingredients': []
                            }
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
                        value={'message': MISSING_ADD_INGREDIENT_MSG},
                        status_codes=[400]
                    ),
                ]
            ),
            401: auth_failed_response,
        }
    )
    def post(self, request: Request) -> Response:
        """
        Create a new UserListIngredients in the database.
        """
        # Extract username from the access token
        username = get_auth_username_from_payload(request=request)
        body = request.data

        if (
            username
            and 'list_name' in body
        ):
            list = create_user_list_ingredients(
                username,
                body['list_name']
            )
            serializer = UserListIngredientsSerializer(list)
        else:
            raise MissingInformation(self.MISSING_CREATE_USER_LIST_MSG)

        return Response({'result': serializer.data}, status=200)

    @extend_schema(
        request=UserListIngredientsViewSerializer,
        responses={
            200: OpenApiResponse(
                response=MessageSerializer,
                examples=[
                    OpenApiExample(
                        name='Item Updated',
                        value={'message': UPDATE_SUCCESS_MSG},
                        status_codes=[200]
                    ),
                    OpenApiExample(
                        name='Referenced Value Does Not Exist',
                        value={'message': DOES_NOT_EXIST_MSG},
                        status_codes=[200]
                    ),
                    OpenApiExample(
                        name='Ingredient Does Not Exist',
                        value={'message': f'{UPDATE_FAILED_MSG} Ingredient does not exist.'},
                        status_codes=[200]
                    ),
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
        }
    )
    def put(self, request: Request) -> Response:
        """
        Adds an ingredient to a user's list.
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
        ):
            result = update_list_ingredient(
                username,
                body['list_name'],
                body['ingredient'],
                body['amount'],
                body['unit']
            )
            status = 200
        else:
            raise MissingInformation(self.MISSING_ADD_INGREDIENT_MSG)

        message = Message(message=result)
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status)


@extend_schema(tags=['Ingredients'])
class AllIngredientsAPIView(APIView):
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
    def get(self, request: Request) -> Response:
        """
        Returns a list of all ingredients in database.
        """
        all_ingredients = get_all_ingredients()
        serializer = IngredientSerializer(all_ingredients, many=True)
        return Response({'result': serializer.data})


@extend_schema(tags=['User'])
class UserAPIView(APIView):
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
                            'result': {
                                'username': 'test_user',
                                'email': 'test_user@domain.com'
                            }
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
    def post(self, request: Request) -> Response:
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

        return Response({'result': serializer.data}, status=201)
