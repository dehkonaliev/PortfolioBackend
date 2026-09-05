from django.shortcuts import render
from .models import (
    CustomUser, Project, Education, Experience, Skill, Language,
    JobTitle, Technology, Field, SkillUnique,
)
from rest_framework.views import APIView
from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q
from baseapp.utils import success_response, error_response, register_usage
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    TempUserSerializer, CreateAccountSerializer, VerifyCodeSerializer,
    LoginSerializer, LogoutSerializer,
    ExperienceSerializer, LanguageSerializer, SkillSerializer,
    EducationSerializer, ProjectSerializer,
    UserProfileSerializer, UserUpdateSettingsSerializer,
    UserSearchSerializer, ChangePasswordSerializer,
    SearchUserResultSerializer, ProjectSearchResultSerializer,
    SkillOrderUpdateSerializer,
)


class CreateTempUserAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = TempUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return success_response(message="Temp user created", data=serializer.data, status_code=201)
    

class VerifyCodeAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = VerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return success_response(message="Code verified", data=serializer.data, status_code=201)
    

class CreateAccountAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CreateAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return success_response(message="Account created", data=serializer.data, status_code=201)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        return success_response(
            message="Login successful",
            data={
                'user': {
                    'id': str(user.id),
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                },
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                },
            },
            status_code=200,
        )


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return success_response(message="Logged out successfully", status_code=200)


class BaseOwnerModelViewSet(mixins.CreateModelMixin,
                            mixins.RetrieveModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.DestroyModelMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    permission_classes = [IsOwnerOrReadOnly]
    usage_map = {}  # list of (lookup_model, lookup_field, serialized_field)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return self.queryset.none()
        owner = self.request.query_params.get('user')
        if owner:
            return self.queryset.filter(user_id=owner)
        return self.queryset.all()

    def perform_create(self, serializer):
        instance = serializer.save(user=self.request.user)
        self._register_usage(instance)

    def perform_update(self, serializer):
        instance = serializer.save()
        self._register_usage(instance)

    def _register_usage(self, instance):
        for model, lookup_field, source_field in self.usage_map:
            value = getattr(instance, source_field, None)
            register_usage(model, lookup_field, value)


class ExperienceViewSet(BaseOwnerModelViewSet):
    queryset = Experience.objects.all().order_by('-created_at')
    serializer_class = ExperienceSerializer
    usage_map = [
        (JobTitle, 'job_title', 'job'),
        (Technology, 'technology', 'company'),
    ]


class LanguageViewSet(BaseOwnerModelViewSet):
    queryset = Language.objects.all().order_by('-created_at')
    serializer_class = LanguageSerializer


class SkillViewSet(BaseOwnerModelViewSet):
    queryset = Skill.objects.all().order_by('-created_at')
    serializer_class = SkillSerializer
    usage_map = [
        (SkillUnique, 'skill', 'name'),
    ]


class EducationViewSet(BaseOwnerModelViewSet):
    queryset = Education.objects.all().order_by('-created_at')
    serializer_class = EducationSerializer
    usage_map = [
        (Field, 'field', 'field'),
    ]


class ProjectViewSet(BaseOwnerModelViewSet):
    queryset = Project.objects.all().order_by('-created_at')
    serializer_class = ProjectSerializer
    usage_map = [
        (Technology, 'technology', 'technologies'),
    ]


class MyProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return success_response(message="My profile", data=serializer.data, status_code=200)


class UserProfileAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, user_id):
        user = CustomUser.objects.filter(id=user_id).first()
        if not user:
            return error_response(message="User not found", status_code=404)
        serializer = UserProfileSerializer(user)
        return success_response(message="User profile", data=serializer.data, status_code=200)


class UserProfileByUsernameAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, username):
        user = CustomUser.objects.filter(username=username).first()
        if not user:
            return error_response(message="User not found", status_code=404)
        serializer = UserProfileSerializer(user)
        return success_response(message="User profile", data=serializer.data, status_code=200)


class UpdateSettingsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = UserUpdateSettingsSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if request.data.get('job_title'):
            register_usage(JobTitle, 'job_title', request.data.get('job_title'))
        return success_response(message="Settings updated", data=serializer.data, status_code=200)


class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(message="Password changed successfully", status_code=200)


class DeleteAccountAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        request.user.delete()
        return success_response(message="Account deleted", status_code=200)


class UserSearchAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        users = CustomUser.objects.all().order_by('-date_joined')

        if query:
            users = users.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(username__icontains=query) |
                Q(job_title__icontains=query) |
                Q(summary__icontains=query)
            )

        serializer = UserSearchSerializer(users, many=True)
        return success_response(message="Users found", data=serializer.data, status_code=200)


class FilterUserSearchAPIView(APIView):
    """
    Advanced filtered user search for employers.
    Query params:
      - skills        : comma-separated skill names (matches any)
      - job_title     : text
      - name          : first/last name text
      - education     : education field text
      - language      : language name text
      - experience    : job/company text
    """
    permission_classes = [AllowAny]

    def get(self, request):
        qs = CustomUser.objects.all().order_by('-date_joined')

        skills = request.query_params.get('skills', '').strip()
        job_title = request.query_params.get('job_title', '').strip()
        name = request.query_params.get('name', '').strip()
        education = request.query_params.get('education', '').strip()
        language = request.query_params.get('language', '').strip()
        experience = request.query_params.get('experience', '').strip()

        if not any([skills, job_title, name, education, language, experience]):
            return success_response(message="Users found", data=[], status_code=200)

        if skills:
            skill_names = [s.strip() for s in skills.split(',') if s.strip()]
            skill_q = Q()
            for sn in skill_names:
                skill_q |= Q(name__icontains=sn)
            skill_user_ids = Skill.objects.filter(skill_q).values_list('user_id', flat=True).distinct()
            qs = qs.filter(id__in=skill_user_ids)

        if job_title:
            qs = qs.filter(job_title__icontains=job_title)

        if name:
            qs = qs.filter(
                Q(first_name__icontains=name) |
                Q(last_name__icontains=name) |
                Q(username__icontains=name)
            )

        if education:
            edu_user_ids = Education.objects.filter(
                Q(field__icontains=education) |
                Q(edu_place__icontains=education)
            ).values_list('user_id', flat=True).distinct()
            qs = qs.filter(id__in=edu_user_ids)

        if language:
            lang_user_ids = Language.objects.filter(
                Q(language__icontains=language) |
                Q(issued_by__icontains=language)
            ).values_list('user_id', flat=True).distinct()
            qs = qs.filter(id__in=lang_user_ids)

        if experience:
            exp_user_ids = Experience.objects.filter(
                Q(job__icontains=experience) |
                Q(company__icontains=experience)
            ).values_list('user_id', flat=True).distinct()
            qs = qs.filter(id__in=exp_user_ids)

        users = list(qs)

        if skills:
            skill_names = [s.strip() for s in skills.split(',') if s.strip()]
            skill_q = Q()
            for sn in skill_names:
                skill_q |= Q(name__icontains=sn)
            for user in users:
                matched = Skill.objects.filter(Q(user=user) & skill_q)
                user._matched_skills = list(matched)

        serializer = SearchUserResultSerializer(users, many=True)
        return success_response(message="Users found", data=serializer.data, status_code=200)


class ProjectSearchAPIView(APIView):
    """
    Separate search for projects. Query params:
      - q        : text in project name / description / technologies
      - skills   : technologies/tech names (comma separated)
    Each project response includes owner info for navigation to the owner page.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        qs = Project.objects.select_related('user').all().order_by('-created_at')

        q = request.query_params.get('q', '').strip()
        skills = request.query_params.get('skills', '').strip()

        if not q and not skills:
            qs = qs.none()

        if q:
            qs = qs.filter(
                Q(name__icontains=q) |
                Q(description__icontains=q) |
                Q(technologies__icontains=q)
            )

        if skills:
            skill_list = [s.strip() for s in skills.split(',') if s.strip()]
            tech_q = Q()
            for s in skill_list:
                tech_q |= Q(technologies__icontains=s)
            qs = qs.filter(tech_q)

        serializer = ProjectSearchResultSerializer(qs, many=True)
        return success_response(message="Projects found", data=serializer.data, status_code=200)


SUGGESTION_MODELS = {
    'job_title': ('JobTitle', 'job_title'),
    'technology': ('Technology', 'technology'),
    'field': ('Field', 'field'),
    'skill': ('SkillUnique', 'skill'),
}


class SuggestionAPIView(APIView):
    """
    Returns suggestion entries for a lookup type, ordered by usage_counts desc.
    Query params:
      - type : job_title | technology | field | skill
      - q    : optional filter text
    """
    permission_classes = [AllowAny]

    def get(self, request):
        key = request.query_params.get('type', '').strip().lower()
        q = request.query_params.get('q', '').strip()

        if key not in SUGGESTION_MODELS:
            return error_response(message="Invalid suggestion type", status_code=400)

        model_name, field_name = SUGGESTION_MODELS[key]
        model_map = {
            'JobTitle': JobTitle,
            'Technology': Technology,
            'Field': Field,
            'SkillUnique': SkillUnique,
        }
        model = model_map[model_name]

        qs = model.objects.all().order_by('-usage_counts', '-created_at')[:50]
        if q:
            filter_kwargs = {f'{field_name}__icontains': q}
            qs = model.objects.filter(**filter_kwargs).order_by('-usage_counts', '-created_at')[:50]

        data = [{field_name: getattr(obj, field_name), 'usage_counts': obj.usage_counts} for obj in qs]
        return success_response(message="Suggestions", data=data, status_code=200)


class ReorderSkillAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request, pk):
        skill = Skill.objects.filter(pk=pk).first()
        if not skill:
            return error_response(message="Skill not found", status_code=404)
        serializer = SkillOrderUpdateSerializer(instance=skill, data=request.data, partial=True,
            context={'request':request, 'skill': skill}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return success_response(message="Reordered")