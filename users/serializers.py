from rest_framework import serializers
from .models import CustomUser, TempUser, MyToken
from baseapp.utils import field_error, code_generate
from baseapp.validators import name_validator, username_validator, password_validator
from django.utils import timezone



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
            temp_user = TempUser.objects.create(email=email, code=code_generate(temp_user.email))
            return temp_user
        elif temp_user and temp_user.expiry_time > timezone.now():
            return temp_user
        
        temp_user = TempUser.objects.create(email=email, code=code_generate(temp_user.email))
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
        return name_validator(first_name)
    
    def validate_last_name(self, last_name):
        return name_validator(last_name)
    
    def validate(self, attrs):
        password = attrs['password']
        conf_password = attrs['conf_password']
        
        password_validator(password)
        
        if password != conf_password:
            return field_error("conf_password", "Confirmation password must identical")
        
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('conf_password')
        validated_data.pop('token')
        
        user = CustomUser.objects.create_user(**validated_data)
        return user
        
        
        
        
        
        
        
        
        