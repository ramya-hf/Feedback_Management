from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration with password validation.
    """
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = (
            'email', 'username', 'first_name', 'last_name',
            'password', 'password_confirm', 'company', 'job_title',
            'phone_number', 'bio'
        )
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'username': {'required': True},
        }
    
    def validate_email(self, value):
        """Validate email uniqueness."""
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()
    
    def validate_username(self, value):
        """Validate username uniqueness."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value
    
    def validate(self, attrs):
        """Validate password confirmation and strength."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Password fields didn't match."})
        
        # Validate password strength
        try:
            validate_password(attrs['password'])
        except ValidationError as e:
            raise serializers.ValidationError({"password": e.messages})
        
        return attrs
    
    def create(self, validated_data):
        """Create user with validated data."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer that includes user information in the response.
    """
    username_field = 'email'
    
    def validate(self, attrs):
        """Validate credentials and return tokens with user info."""
        data = super().validate(attrs)
        
        # Add user information to the token response
        data.update({
            'user': {
                'id': self.user.id,
                'email': self.user.email,
                'username': self.user.username,
                'first_name': self.user.first_name,
                'last_name': self.user.last_name,
                'role': self.user.role,
                'avatar': self.user.avatar.url if self.user.avatar else None,
                'is_email_verified': self.user.is_email_verified,
            }
        })
        
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile information (read/update).
    """
    full_name = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'full_name',
            'role', 'avatar', 'avatar_url', 'bio', 'phone_number', 'company',
            'job_title', 'is_email_verified', 'email_notifications',
            'date_joined', 'last_login', 'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'email', 'username', 'role', 'date_joined', 'last_login',
            'created_at', 'updated_at', 'is_email_verified'
        )
    
    def get_full_name(self, obj):
        """Return user's full name."""
        return obj.get_full_name()
    
    def get_avatar_url(self, obj):
        """Return avatar URL if exists."""
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None


class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing users (minimal information).
    """
    full_name = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'full_name',
            'role', 'avatar_url', 'company', 'job_title', 'is_active',
            'date_joined', 'last_login'
        )
    
    def get_full_name(self, obj):
        """Return user's full name."""
        return obj.get_full_name()
    
    def get_avatar_url(self, obj):
        """Return avatar URL if exists."""
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for changing user password.
    """
    old_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    
    def validate_old_password(self, value):
        """Validate the old password."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value
    
    def validate(self, attrs):
        """Validate new password confirmation and strength."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "Password fields didn't match."})
        
        # Validate password strength
        try:
            validate_password(attrs['new_password'])
        except ValidationError as e:
            raise serializers.ValidationError({"new_password": e.messages})
        
        return attrs
    
    def save(self):
        """Change user password."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class UserRoleUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user roles (admin only).
    """
    class Meta:
        model = User
        fields = ('role',)
    
    def validate_role(self, value):
        """Validate role assignment."""
        request = self.context.get('request')
        if request and request.user:
            # Only admins can change roles
            if not request.user.is_admin:
                raise serializers.ValidationError("Only administrators can change user roles.")
            
            # Prevent users from removing their own admin status
            if (self.instance == request.user and 
                self.instance.role == User.Role.ADMIN and 
                value != User.Role.ADMIN):
                raise serializers.ValidationError("You cannot remove your own admin privileges.")
        
        return value 