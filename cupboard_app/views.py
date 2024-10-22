from drf_spectacular.utils import (
    extend_schema
)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView, exception_handler

from utils.api_helper import (
    get_auth_username_from_payload,
    get_auth_email_from_payload
)
from utils.permissions import (
    HasMessagesPermission
)
from cupboard_app.models import Message
from cupboard_app.queries import (
    get_all_ingredients,
    create_user
)
from cupboard_app.serializers import (
    MessageSerializer,
    IngredientSerializer
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
    if response.status_code == 403:
        response.data = {
            'error': 'insufficient_permissions',
            'error_description': response.data.get('detail', 'API Error'),
            'message': 'Permission denied'
        }
    elif response and isinstance(response.data, dict):
        response.data = {'message': response.data.get('detail', 'API Error')}
    else:
        response.data = {'message': 'API Error'}
    return response


class PublicMessageAPIView(APIView):
    permission_classes = [AllowAny]
    text = "Hello from a public endpoint! You don't need to be authenticated to see this."

    @extend_schema(
        request=None,
        responses={
            200: MessageSerializer,
            401: MessageSerializer
        }
    )
    def get(self, request: Request) -> Response:
        """
        This is an example of a public message API request.
        """
        message = Message(message=self.text)
        serializer = MessageSerializer(message)
        return Response(serializer.data)


class PrivateMessageAPIView(APIView):
    text = "Hello from a private endpoint! You need to be authenticated to see this."

    @extend_schema(
        request=None,
        responses={
            200: MessageSerializer,
            401: MessageSerializer
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


class PrivateScopedMessageAPIView(APIView):
    permission_classes = [HasMessagesPermission]
    text = (
        "Hello from a private endpoint! You need to be authenticated "
        "and have a permission of read:messages to see this."
    )

    @extend_schema(
        request=None,
        responses={
            201: MessageSerializer,
            401: MessageSerializer
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


class AllIngredientsAPIView(APIView):
    @extend_schema(
        request=None,
        responses={
            200: IngredientSerializer,
            401: MessageSerializer
        }
    )
    def get(self, request: Request) -> Response:
        """
        Returns a list of all ingredients in database.
        """
        all_ingredients = get_all_ingredients()
        serializer = IngredientSerializer(all_ingredients, many=True)
        return Response({"result": serializer.data})


class UserAPIView(APIView):
    @extend_schema(
        request=None,
        responses={
            200: MessageSerializer,
            401: MessageSerializer,
            500: MessageSerializer,
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
            # Try creating user in the db
            response = create_user(username=username, email=email)
            status = 200
        else:
            response = 'Username or email missing. Unable to create new user.'
            status = 500

        message = Message(message=response)
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status)
