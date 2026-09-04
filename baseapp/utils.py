from rest_framework import serializers
from rest_framework.response import Response
import secrets
from random import randint
from django.db.models import F


def register_usage(model, field, values):
    """Register one or more lookup entries, incrementing usage_counts.

    `values` may be a comma-separated string or a plain value. Existing
    entries are reused (never duplicated) and simply bumped; new entries
    are created.
    """
    if values is None:
        return
    entries = []
    if isinstance(values, str):
        entries = [v.strip() for v in values.split(',') if v.strip()]
    else:
        entries = [str(values).strip()]

    for entry in entries:
        if not entry:
            continue
        try:
            obj, _ = model.objects.get_or_create(**{field: entry})
            model.objects.filter(pk=obj.pk).update(usage_counts=F('usage_counts') + 1)
        except Exception:
            # lookup registration must never break the main save flow
            continue

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