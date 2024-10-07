from functools import wraps

from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request

from .utils import jwt_decode_token
from .queries import get_all_ingredients as queries_get_all_ingredients
from .queries import get_listName_id as queries_get_listName_id
from .queries import get_user_id as queries_get_user_id
from .queries import get_measurement_id as queries_get_measurment_id
from .queries import get_ingredient_id as queries_get_ingredient_id

import json

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

# Gets all possible ingredients in db
# Output Format:
#{
#      "result":[
#        {
#            "name":"ingredient_1"
#            "type":"ingredient_type"
#        },
#        {
#            "name":"ingredient_2"
#            "type":"ingredint_type2"
#        }
#      ]
#   }
@api_view(['GET'])
def get_all_ingredients(request):
    all_ingredients = queries_get_all_ingredients() # runs the query for getting all ingredients
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

# Adds ingredients specified to list specified, if it exists
# Output Format for success:
#{
#   "result":"success",
#}
#
# Output Format for failure
# each of the entries after "result" is either True or False depending of if
# the item can be found in the db
#{
#   "result":"failure",
#   'username':[True or False],
#   'listName':[True or False],
#   'ingredient':[True or False],
#   'unit':[True or False]
#}
#
# TODO MAKE THIS PUBLiC SO THAT THEN WE CAN JUST ACCESS IT FROM ANYWHERE, THen I GUES MAKE A POST REQUEST OVER CMD TO TEST IF IT ACUTALLY FUNCTIONS AS EXPECTED
@api_view(['POST'])
def add_ingredient(request):
    if(request.method == 'POST'):
        if(request.body == None):
            print("REQUEST BODY IS EMPTY!!!!!!!!!")
        else:
            print("REQUEST BODY: " + str(request.body))
        requestDict = request.data.dict() #converts querydict to dict

        #Gets ids of all items to ensure thier existence
        userID = queries_get_user_id(requestDict['username'])
        listID = queries_get_listName_id(requestDict['listName'])
        ingID = queries_get_ingredient_id(requestDict['ingredient'])
        measureID = queries_get_measurment_id(requestDict['unit'])

        #Adds the ingredient to the list if all required compenents are found
        if(
            userID!= None
            and listID != None
            and ingID != None
            and measureID != None
        ):
            insert_list_ingredient(requestDict['username'], requestDict['listName'], requestDict['ingredient'], requestDict['amount'], requestDict['unit'])

            return JsonResponse(
                {
                    'result':'succes'
                }
            )

        #returns failure if any of the required items cannot be found in the db
        else:
            return JsonResponse(
                {
                    'result':'failure',
                    'username':str(userID!=None),
                    'listName':str(listID!=None),
                    'ingredient':str(ingID!=None),
                    'unit':str(measureID!=None)
                },
                status=500
            )
