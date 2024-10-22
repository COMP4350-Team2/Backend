import os
import json

from django.http import JsonResponse
from authlib.integrations.django_oauth2 import ResourceProtector
from rest_framework.request import Request
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes

from cupboard_app.validator import (
    TestBearerTokenValidator,
    Auth0JWTBearerTokenValidator
)
from cupboard_app.utils import (
    decode_auth_access_token,
    get_auth_access_token_from_header,
    get_auth_username_from_payload
)
from cupboard_app.queries import (
    get_all_ingredients as queries_get_all_ingredients,
    update_list_ingredient as queries_update_list_ingredient,
    create_user as queries_create_user,
)


# Environment Variables
DEV_LAYER = os.getenv('DEV_LAYER')
TEST_RUN = os.getenv('TEST_RUN')
TEST_KEY = os.getenv('TEST_KEY')
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
AUTH0_API_IDENTIFIER = os.getenv('AUTH0_API_IDENTIFIER')


# Set validator
require_auth = ResourceProtector()
if DEV_LAYER == 'mock' or TEST_RUN == 'true':
    validator = TestBearerTokenValidator(
        AUTH0_DOMAIN,
        AUTH0_API_IDENTIFIER
    )
else:
    validator = Auth0JWTBearerTokenValidator(
        AUTH0_DOMAIN,
        AUTH0_API_IDENTIFIER
    )
require_auth.register_token_validator(validator)


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
@require_auth(None)
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
@require_auth("read:messages")
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
@require_auth(None)
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
@require_auth(None)
def create_user(request: Request) -> JsonResponse:
    """
    Create a new user in the database based on auth0 user

    Args:
        request: The rest framework Request object with access token

    Returns:
        A json object with the message of the create user result.
    """
    # Get access token and payload from the request
    token = get_auth_access_token_from_header(request=request)
    payload = decode_auth_access_token(token=token)

    # Extract username and email from payload
    username = get_auth_username_from_payload(payload=payload)
    email = payload.get('https://cupboard-teacup.com/email')

    if email and username:
        # Try creating user in the db
        response = queries_create_user(username=username, email=email)
        status = 200
    else:
        response = 'Username or email missing. Unable to create new user.'
        status = 500

    return JsonResponse(dict(message=response), status=status)


@api_view(['POST'])
@require_auth(None)
def add_ingredient_to_list(request: Request) -> JsonResponse:
    """
    adds an ingredient to a list

    Args:
        request: The rest framework Request post object containing json in the following format
        {
            username: [USERNAME],
            listName: [LISTNAME],
            ingredient: [INGREDIENT],
            amount: [AMOUNT/QUANTITY],
            unit: [MEASURMENT UNIT]
        }

    Returns:
        A json object with the result of the operation.
        Output Format:
        {
            "result": [RESULT MSG]
        }
    """

    body = json.loads(request.body)

    if(
        'username' in body
        and 'listName' in body
        and 'ingredient' in body
        and 'amount' in body
        and 'unit' in body
    ):
        result = queries_update_list_ingredient(body['username'], body['listName'], body['ingredient'], body['amount'], body['unit'])
    else:
        result = "Required value misssing from sent request, please ensure all items are sent in the following format: {\n  username: [USERNAME],\n  listName: [LISTNAME],\n  ingredient: [INGREDIENT],\n  amount: [AMOUNT/QUANTITY],\n  unit: [MEASURMENT UNIT]\n}"
    # Runs the query for getting all ingredients
   
    return JsonResponse(
        {
            'result': result
        }
    )


