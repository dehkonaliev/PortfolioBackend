from rest_framework import serializers
from .models import CustomUser, TempUser, MyToken, Experience, Language, Skill, Education, Project
from baseapp.utils import field_error, code_generate
from baseapp.validators import name_validator, username_validator, password_validator
from django.contrib.auth import authenticate
from django.utils import timezone
from django.db.models import F



class TempUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TempUser
        fields = ['id', 'email']
        read_only_fields = ['id']
        
    def create(self, validated_data):
        email = validated_data['email']
        if CustomUser.objects.filter(email=email).exists():
            return field_error("email", "A user with this email already exists")
        temp_user = TempUser.objects.filter(email=email).first()
        if temp_user and temp_user.expiry_time <= timezone.now():
            temp_user.delete()
            temp_user = TempUser.objects.create(email=email, code=code_generate(email))
            return temp_user
        elif temp_user and temp_user.expiry_time > timezone.now():
            return temp_user

        temp_user = TempUser.objects.create(email=email, code=code_generate(email))
        return temp_user
        

class VerifyCodeSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=32, required=False)
    class Meta:
        model = TempUser
        fields = ['id', 'email', 'code', 'token']
        read_only_fields = ['id', 'token']
        
    def validate_email(self, email):
        email = email.strip()
        temp_user = TempUser.objects.filter(email=email).first()
        if not temp_user:
            return field_error("email", "A user with that email not found")
        if temp_user and temp_user.expiry_time <= timezone.now():
            return field_error("email", "Code expired")
        
        return email
    
    def validate(self, attrs):
        code = attrs['code']
        email = attrs['email']
        
        temp_user = TempUser.objects.filter(email=email).first()
        if temp_user.code != code:
            return field_error("code", "Invalid code")
        
        attrs['temp_user'] = temp_user
        
        return attrs
    
    def create(self, validated_data):
        temp_user = validated_data['temp_user']
        token = MyToken.objects.create(temp_user=temp_user)
        validated_data['token'] = token.token
        
        return validated_data
    
    
class CreateAccountSerializer(serializers.ModelSerializer):
    token = serializers.CharField(write_only=True)
    conf_password = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    class Meta:
        model = CustomUser
        fields = ['id', 'token', 'username', 'first_name', 'last_name', 'conf_password', 'password']
        read_only_fields = ['id']
        
    def validate_token(self, token):
        token_obj = MyToken.objects.filter(token=token).first()
        if not token_obj:
            return field_error("token", "Token not found")
        return token_obj
    
    def validate_username(self, username):
        return username_validator(username)
    
    def validate_first_name(self, first_name):
        return name_validator(first_name, "first_name")
    
    def validate_last_name(self, last_name):
        return name_validator(last_name, "last_name")
    
    def validate(self, attrs):
        password = attrs['password']
        conf_password = attrs['conf_password']
        
        password_validator(password)
        
        if password != conf_password:
            return field_error("conf_password", "Confirmation password must identical")
        
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('conf_password')
        token_email = validated_data['token'].temp_user.email
        TempUser.objects.filter(email=token_email).delete()
        validated_data.pop('token', None)
        
        validated_data['email'] = token_email
        
        user = CustomUser.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        user = authenticate(username=username, password=password)
        if not user:
            return field_error("credentials", "Invalid username or password.")
        if not user.is_active:
            return field_error("credentials", "User account is disabled.")
        attrs['user'] = user
        return attrs


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate_refresh(self, value):
        from rest_framework_simplejwt.tokens import RefreshToken
        try:
            token = RefreshToken(value)
            token.blacklist()
        except Exception:
            return field_error("refresh", "Token is invalid or already blacklisted.")
        return value


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = ['id', 'job', 'company', 'activity', 'from_date', 'to_date', 'location', 'created_at']
        read_only_fields = ['id', 'created_at']


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = ['id', 'language', 'level', 'issued_by', 'created_at']
        read_only_fields = ['id', 'created_at']


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'level', 'order']
        read_only_fields = ['id']


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ['id', 'field', 'edu_place', 'from_date', 'to_date', 'what_learnt', 'certification', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'technologies', 'cover_image', 'url', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserProfileSerializer(serializers.ModelSerializer):
    experiences = serializers.SerializerMethodField()
    languages = serializers.SerializerMethodField()
    skills = serializers.SerializerMethodField()
    educations = serializers.SerializerMethodField()
    projects = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email',
            'job_title', 'summary', 'address', 'phone_number', 'linkedin_url', 'telegram_url',
            'profile_photo', 'profile_thumbnail',
            'experiences', 'languages', 'skills', 'educations', 'projects',
        ]
        read_only_fields = ['id', 'username', 'email', 'profile_thumbnail']

    def get_experiences(self, obj):
        return ExperienceSerializer(obj.experiences.all().order_by('-created_at'), many=True).data

    def get_languages(self, obj):
        return LanguageSerializer(obj.languages.all().order_by('-created_at'), many=True).data

    def get_skills(self, obj):
        return SkillSerializer(obj.skills.all().order_by('order'), many=True).data

    def get_educations(self, obj):
        return EducationSerializer(obj.educations.all().order_by('-created_at'), many=True).data

    def get_projects(self, obj):
        return ProjectSerializer(obj.projects.all().order_by('-created_at'), many=True).data


class UserUpdateSettingsSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'job_title', 'summary', 'email',
            'address', 'phone_number', 'linkedin_url', 'telegram_url', 'profile_photo',
        ]

    def validate_first_name(self, first_name):
        if first_name and first_name.strip():
            return name_validator(first_name, "first_name")
        return first_name

    def validate_last_name(self, last_name):
        if last_name and last_name.strip():
            return name_validator(last_name, "last_name")
        return last_name

    def validate_email(self, email):
        email = (email or '').strip()
        if not email:
            return field_error("email", "Email cannot be blank.")
        queryset = CustomUser.objects.filter(email__iexact=email)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            return field_error("email", "A user with this email already exists.")
        return email


class UserSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'first_name', 'last_name', 'job_title',
            'summary', 'profile_thumbnail', 'profile_photo', 'address',
        ]


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    conf_password = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            return field_error("current_password", "Current password is incorrect.")
        return value

    def validate(self, attrs):
        new_password = attrs.get('new_password')
        conf_password = attrs.get('conf_password')

        password_validator(new_password)

        if new_password != conf_password:
            return field_error("conf_password", "Confirmation password must be identical.")

        return attrs

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class SearchUserNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'level']


class SearchProjectNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'technologies', 'cover_image', 'url']


class SearchUserResultSerializer(serializers.ModelSerializer):
    matched_skills = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'first_name', 'last_name', 'job_title',
            'summary', 'profile_photo', 'profile_thumbnail', 'address',
            'matched_skills',
        ]

    def get_matched_skills(self, obj):
        skills = getattr(obj, '_matched_skills', [])
        return SearchUserNestedSerializer(skills, many=True).data if isinstance(skills, list) else skills


class UserSearchFilterSerializer(UserSearchSerializer):
    matched_skills = serializers.SerializerMethodField()

    class Meta(UserSearchSerializer.Meta):
        fields = UserSearchSerializer.Meta.fields + ['matched_skills']

    def get_matched_skills(self, obj):
        skills = getattr(obj, '_matched_skills', [])
        return SearchUserNestedSerializer(skills, many=True).data if isinstance(skills, list) else skills


class ProjectSearchResultSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'technologies', 'cover_image',
            'url', 'created_at', 'owner',
        ]

    def get_owner(self, obj):
        return {
            'id': str(obj.user.id),
            'username': obj.user.username,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
            'job_title': obj.user.job_title,
            'profile_thumbnail': obj.user.profile_thumbnail.url if obj.user.profile_thumbnail else None,
        }
        

class SkillOrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['order']
        
    def validate(self, attrs):
        order = attrs['order']
        
        if order < 0:
            return field_error("order", "Order cannot be negative number")
        
        return attrs
    
    def update(self, instance, validated_data):
        order = validated_data['order']
        user = self.context.get('request').user
        skill = self.context.get('skill')
        
        skill.order = order
        skill.save()
        
        Skill.objects.filter(user=user, order__gt=order-1).update(order=F('order')+1)
        
        return skill