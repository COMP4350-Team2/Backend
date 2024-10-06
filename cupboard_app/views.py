from functools import wraps

from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request

from .utils import jwt_decode_token

CRED_NOT_PROVIDED = {'detail': 'Authentication credentials were not provided.'}
TOKEN_DECODE_ERROR = {'detail': 'Error decoding token.'}


def get_token_auth_header(request: Request) -> str:
    """
    Obtains the Access Token from the Authorization Header

    Args:
        request: The rest_framework Request object

    Returns:
        The access token from the request.
    """
    auth = request.META.get("HTTP_AUTHORIZATION", None)
    parts = auth.split()
    token = parts[1]

    return token


def requires_scope(required_scope: str):
    """
    Determines if the required scope is present in the Access Token

    Args:
        required_scope: The scope required to access the resource that we are looking for

    Returns:
        A decorator function that checks for the scope in the token
    """
    def require_scope(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = get_token_auth_header(args[0])
            decoded = jwt_decode_token(token)
            if decoded.get("scope"):
                token_scopes = decoded["scope"].split()
                for token_scope in token_scopes:
                    if token_scope == required_scope:
                        return f(*args, **kwargs)
            response = JsonResponse({'message': 'You don\'t have access to this resource'})
            response.status_code = 403
            return response
        return decorated
    return require_scope


@api_view(['GET'])
@permission_classes([AllowAny])
def public(request: Request) -> JsonResponse:
    """
    Example of public api request.

    Args:
        request: The rest_framework Request object

    Returns:
        A json object with the message from public.
    """
    return JsonResponse(
        {
            'message': (
                'Hello from a public endpoint! '
                'You don\'t need to be authenticated to see this.'
            )
        }
    )


@api_view(['GET'])
def private(request: Request) -> JsonResponse:
    """
    Example of private api request.

    Args:
        request: The rest_framework Request object with access token

    Returns:
        A json object with the message from private.
    """
    return JsonResponse(
        {
            'message': (
                'Hello from a private endpoint! '
                'You need to be authenticated to see this.'
            )
        }
    )


@api_view(['GET'])
@requires_scope('read:messages')
def private_scoped(request: Request) -> JsonResponse:
    """
    Example of private-scoped api request.

    Args:
        request: The rest_framework Request object with access token
                 containing a scope "read:messages".

    Returns:
        A json object with the message from private-scoped.
    """
    return JsonResponse(
        {
            'message': (
                'Hello from a private endpoint! '
                'You need to be authenticated and have a scope of '
                'read:messages to see this.'
            )
        }
    )
