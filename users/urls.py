from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CreateTempUserAPIView, CreateAccountAPIView, VerifyCodeAPIView,
    LoginAPIView, LogoutAPIView,
    ExperienceViewSet, LanguageViewSet, SkillViewSet,
    EducationViewSet, ProjectViewSet,
    MyProfileAPIView, UserProfileAPIView, UserProfileByUsernameAPIView,
    UpdateSettingsAPIView,
    ChangePasswordAPIView, DeleteAccountAPIView, UserSearchAPIView,
    FilterUserSearchAPIView, ProjectSearchAPIView,
    SuggestionAPIView, ReorderSkillAPIView
)


router = DefaultRouter()
router.register('experiences', ExperienceViewSet, basename='experience')
router.register('languages', LanguageViewSet, basename='language')
router.register('skills', SkillViewSet, basename='skill')
router.register('educations', EducationViewSet, basename='education')
router.register('projects', ProjectViewSet, basename='project')


urlpatterns = [
    path('signup', CreateTempUserAPIView.as_view()),
    path('verify-code', VerifyCodeAPIView.as_view()),
    path('create-account', CreateAccountAPIView.as_view()),
    path('login', LoginAPIView.as_view()),
    path('logout', LogoutAPIView.as_view()),
    path('token/refresh', TokenRefreshView.as_view()),

    path('me', MyProfileAPIView.as_view()),
    path('user/<uuid:user_id>', UserProfileAPIView.as_view()),
    path('user/<str:username>', UserProfileByUsernameAPIView.as_view()),
    path('users/search', UserSearchAPIView.as_view()),
    path('users/filter', FilterUserSearchAPIView.as_view()),
    path('projects/search', ProjectSearchAPIView.as_view()),
    path('suggestions', SuggestionAPIView.as_view()),
    path('settings', UpdateSettingsAPIView.as_view()),
    path('change-password', ChangePasswordAPIView.as_view()),
    path('delete-account', DeleteAccountAPIView.as_view()),
    path('reorder-skill/<uuid:pk>', ReorderSkillAPIView.as_view()),

    path('', include(router.urls)),
]