from django.shortcuts import render
from .models import CustomUser, Project, Education, Experience, Skill, Language
from rest_framework.views import APIView
from baseapp.utils import success_response, error_response
from .serializers import (TempUserSerializer, CreateAccountSerializer, VerifyCodeSerializer

)


class CreateTempUserAPIView(APIView):
    def post(self, request):
        serializer = TempUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return success_response(message="Temp user created", data=serializer.data, status_code=201)
    

class VerifyCodeAPIView(APIView):
    def post(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return success_response(message="Code verified", data=serializer.data, status_code=201)
    

class CreateAccountAPIView(APIView):
    def post(self, request):
        serializer = CreateAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return success_response(message="Account created", data=serializer.data, status_code=201)
    
