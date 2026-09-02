from rest_framework import serializers
from rest_framework.response import Response
import secrets
from random import randint

def field_error(field, message):
    raise serializers.ValidationError({field:message})

def success_response(message="Successfull", data=None, status_code=200):
    return Response({
        'success': True,
        "message": message,
        'data': data
    }, status=status_code)

def error_response(message="Failed", data=None, status_code=400):
    return Response({
        'success': False,
        "message": message,
        'data': data
    }, status=status_code)
    
def code_generate(user_email):
    return secrets.randbelow(900000) + 100000