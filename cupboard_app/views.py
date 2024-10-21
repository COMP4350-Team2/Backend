import json

from django.http import JsonResponse
from rest_framework.request import Request
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import exception_handler

from utils.api_helper import (
    get_auth_username_from_payload,
    get_auth_email_from_payload
)
from utils.permissions import (
    HasMessagesPermission
)
from cupboard_app.queries import (
    get_all_ingredients as queries_get_all_ingredients,
    create_user as queries_create_user,
)


def api_exception_handler(exc, context=None) -> JsonResponse:
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


@api_view(['GET'])
@permission_classes([AllowAny])
def public(request: Request) -> JsonResponse:
    """
    Example of public api request.

    Args:
        request: The rest framework Request object

    Returns:
        A json object with the message from public.
    """
    response = "Hello from a public endpoint! You don't need to be authenticated to see this."
    return JsonResponse(dict(message=response))


@api_view(['GET'])
def private(request: Request) -> JsonResponse:
    """
    Example of private api request. A valid access token is required to access this route

    Args:
        request: The rest framework Request object with access token

    Returns:
        A json object with the message from private.
    """
    response = "Hello from a private endpoint! You need to be authenticated to see this."
    return JsonResponse(dict(message=response))


@api_view(['GET'])
@permission_classes([HasMessagesPermission])
def private_scoped(request: Request) -> JsonResponse:
    """
    Example of private-scoped api request. A valid access token and an appropriate scope
    are required to access this route.

    Args:
        request: The rest framework Request object with access token containing a scope
                "read:messages".

    Returns:
        A json object with the message from private-scoped.
    """
    response = (
        "Hello from a private endpoint! You need to be authenticated "
        "and have a scope of read:messages to see this."
    )
    return JsonResponse(dict(message=response))


# API Views - Get requests
@api_view(['GET'])
def get_all_ingredients(request: Request) -> JsonResponse:
    """
    Gets all possible ingredients in db

    Args:
        request: The rest framework Request object with access token

    Returns:
        A json object with the ingredients as a result.
        Output Format:
        {
            "result": [
                {
                    "name":"ingredient_1"
                    "type":"ingredient_type"
                },
                {
                    "name":"ingredient_2"
                    "type":"ingredint_type2"
                }
            ]
        }
    """
    # Runs the query for getting all ingredients
    all_ingredients = queries_get_all_ingredients()
    converted_ingredients = []
    for ing in all_ingredients:
        converted_ingredients.append(json.loads(str(ing)))
    return JsonResponse(
        {
            'result': (
                converted_ingredients
            )
        }
    )


# API Views - Post requests
@api_view(['POST'])
def create_user(request: Request) -> JsonResponse:
    """
    Create a new user in the database based on auth0 user

    Args:
        request: The rest framework Request object with access token

    Returns:
        A json object with the message of the create user result.
    """
    # Extract username and email
    username = get_auth_username_from_payload(request=request)
    email = get_auth_email_from_payload(request=request)

    if email and username:
        # Try creating user in the db
        response = queries_create_user(username=username, email=email)
        status = 200
    else:
        response = 'Username or email missing. Unable to create new user.'
        status = 500

    return JsonResponse(dict(message=response), status=status)
