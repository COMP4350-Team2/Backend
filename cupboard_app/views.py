from functools import wraps
import jwt

from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from .queries import get_all_ingredients as queries_get_all_ingredients
import json

def get_token_auth_header(request):
    """
    Obtains the Access Token from the Authorization Header
    """
    auth = request.META.get("HTTP_AUTHORIZATION", None)
    parts = auth.split()
    token = parts[1]

    return token


def requires_scope(required_scope):
    """
    Determines if the required scope is present in the Access Token

    Args:
        required_scope (str): The scope required to access the resource
    """
    def require_scope(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = get_token_auth_header(args[0])
            decoded = jwt.decode(token, verify=False)
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
def public(request):
    return JsonResponse(
        {
            'message': (
                'Hello from a public endpoint! '
                'You don\'t need to be authenticated to see this.'
            )
        }
    )


@api_view(['GET'])
def private(request):
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
def private_scoped(request):
    return JsonResponse(
        {
            'message': (
                'Hello from a private endpoint! '
                'You need to be authenticated and have a scope of '
                'read:messages to see this.'
            )
        }
    )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_ingredients(request):
    return get_all_ingredients_worker()

# Gets all ingredients and returns, accepts mockData (triggering )
def get_all_ingredients_worker(mockData = None):
    if(mockData != None):
        return JsonResponse(
            {
                'result': (
                    mockData
                )
            }
        )
    else:
        all_ingredients = queries_get_all_ingredients() # runs the query for getting all ingredients
        converted_ingredients = []
        for ing in all_ingredients:
            converted_ingredients.append(json.loads(ing))
        return JsonResponse(
            {
                'result': (
                    converted_ingredients
                )
            }
        )
