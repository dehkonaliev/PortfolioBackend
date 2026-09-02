from django.urls import path
from .views import CreateTempUserAPIView, CreateAccountAPIView, VerifyCodeAPIView


urlpatterns = [
    path('signup', CreateTempUserAPIView.as_view()),
    path('verify-code', VerifyCodeAPIView.as_view()),
    path('create-account', CreateAccountAPIView.as_view()),
]