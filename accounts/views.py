from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import logout
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import User
from .serializers import (
    UserRegistrationSerializer,
    CustomTokenObtainPairSerializer,
    UserProfileSerializer,
    UserListSerializer,
    PasswordChangeSerializer,
    UserRoleUpdateSerializer
)


class UserRegistrationView(generics.CreateAPIView):
    """
    API view for user registration.
    
    POST /api/auth/register/
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def perform_create(self, serializer):
        """Create user and return success response."""
        user = serializer.save()
        return user


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token obtain view that includes user information.
    
    POST /api/auth/login/
    """
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]


class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom JWT token refresh view.
    
    POST /api/auth/refresh/
    """
    permission_classes = [permissions.AllowAny]


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """
    Logout view that blacklists the refresh token.
    
    POST /api/auth/logout/
    """
    try:
        refresh_token = request.data.get("refresh_token")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        logout(request)
        return Response(
            {"message": "Successfully logged out."},
            status=status.HTTP_205_RESET_CONTENT
        )
    except Exception as e:
        return Response(
            {"error": "Invalid token or logout failed."},
            status=status.HTTP_400_BAD_REQUEST
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API view for retrieving and updating user profile.
    
    GET /api/auth/profile/
    PUT /api/auth/profile/
    PATCH /api/auth/profile/
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Return the current user."""
        return self.request.user


class UserListView(generics.ListAPIView):
    """
    API view for listing users (admin and moderator only).
    
    GET /api/auth/users/
    """
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'is_active', 'is_email_verified']
    search_fields = ['email', 'first_name', 'last_name', 'username', 'company']
    ordering_fields = ['created_at', 'last_login', 'email', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter queryset based on user permissions."""
        user = self.request.user
        queryset = super().get_queryset()
        
        # Only admins and moderators can view all users
        if not user.can_moderate:
            # Contributors can only see other contributors
            queryset = queryset.filter(role=User.Role.CONTRIBUTOR)
        
        return queryset


class UserDetailView(generics.RetrieveUpdateAPIView):
    """
    API view for retrieving and updating specific user details (admin only).
    
    GET /api/auth/users/{id}/
    PUT /api/auth/users/{id}/
    PATCH /api/auth/users/{id}/
    """
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        """Different permissions for different actions."""
        if self.request.method in ['PUT', 'PATCH']:
            # Only admins can update other users
            permission_classes = [permissions.IsAuthenticated]
        else:
            # Moderators can view user details
            permission_classes = [permissions.IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def check_object_permissions(self, request, obj):
        """Check if user can access this object."""
        user = request.user
        
        # Users can access their own profile
        if obj == user:
            return
        
        # Only admins and moderators can access other user profiles
        if not user.can_moderate:
            self.permission_denied(
                request,
                message="You don't have permission to access this user's profile."
            )
        
        # Only admins can update other users
        if request.method in ['PUT', 'PATCH'] and not user.is_admin:
            self.permission_denied(
                request,
                message="Only administrators can update user profiles."
            )


class PasswordChangeView(generics.GenericAPIView):
    """
    API view for changing user password.
    
    POST /api/auth/change-password/
    """
    serializer_class = PasswordChangeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        """Change user password."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.save()
        
        return Response(
            {"message": "Password has been changed successfully."},
            status=status.HTTP_200_OK
        )


class UserRoleUpdateView(generics.UpdateAPIView):
    """
    API view for updating user roles (admin only).
    
    PATCH /api/auth/users/{id}/role/
    """
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserRoleUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def check_object_permissions(self, request, obj):
        """Only admins can change user roles."""
        if not request.user.is_admin:
            self.permission_denied(
                request,
                message="Only administrators can change user roles."
            )


class UserDeactivateView(generics.UpdateAPIView):
    """
    API view for deactivating users (admin only).
    
    PATCH /api/auth/users/{id}/deactivate/
    """
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def patch(self, request, *args, **kwargs):
        """Deactivate user account."""
        user = self.get_object()
        
        # Only admins can deactivate users
        if not request.user.is_admin:
            return Response(
                {"error": "Only administrators can deactivate users."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Prevent users from deactivating themselves
        if user == request.user:
            return Response(
                {"error": "You cannot deactivate your own account."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.is_active = False
        user.save()
        
        return Response(
            {"message": f"User {user.email} has been deactivated."},
            status=status.HTTP_200_OK
        )


class UserActivateView(generics.UpdateAPIView):
    """
    API view for activating users (admin only).
    
    PATCH /api/auth/users/{id}/activate/
    """
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def patch(self, request, *args, **kwargs):
        """Activate user account."""
        user = self.get_object()
        
        # Only admins can activate users
        if not request.user.is_admin:
            return Response(
                {"error": "Only administrators can activate users."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user.is_active = True
        user.save()
        
        return Response(
            {"message": f"User {user.email} has been activated."},
            status=status.HTTP_200_OK
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_stats_view(request):
    """
    API view for getting user statistics (admin and moderator only).
    
    GET /api/auth/stats/
    """
    user = request.user
    
    # Only admins and moderators can view stats
    if not user.can_moderate:
        return Response(
            {"error": "You don't have permission to view user statistics."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    stats = {
        "total_users": User.objects.count(),
        "active_users": User.objects.filter(is_active=True).count(),
        "inactive_users": User.objects.filter(is_active=False).count(),
        "verified_users": User.objects.filter(is_email_verified=True).count(),
        "unverified_users": User.objects.filter(is_email_verified=False).count(),
        "admins": User.objects.filter(role=User.Role.ADMIN, is_active=True).count(),
        "moderators": User.objects.filter(role=User.Role.MODERATOR, is_active=True).count(),
        "contributors": User.objects.filter(role=User.Role.CONTRIBUTOR, is_active=True).count(),
    }
    
    return Response(stats, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def current_user_view(request):
    """
    API view for getting current user information.
    
    GET /api/auth/me/
    """
    serializer = UserProfileSerializer(request.user, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)
