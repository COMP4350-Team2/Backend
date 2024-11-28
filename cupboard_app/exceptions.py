from rest_framework.exceptions import APIException


class MissingInformation(APIException):
    status_code = 400
    default_detail = 'Bad request, missing information. Please provide all the information.'
    default_code = 'bad_request'


class FailedOperation(APIException):
    status_code = 400
    default_detail = 'Bad request, operation failed.'
    default_code = 'bad_request'
