from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication endpoints
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.CustomTokenObtainPairView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('refresh/', views.CustomTokenRefreshView.as_view(), name='token_refresh'),
    
    # User profile endpoints
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('me/', views.current_user_view, name='current-user'),
    path('change-password/', views.PasswordChangeView.as_view(), name='change-password'),
    
    # User management endpoints (admin/moderator)
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('users/<int:pk>/role/', views.UserRoleUpdateView.as_view(), name='user-role-update'),
    path('users/<int:pk>/deactivate/', views.UserDeactivateView.as_view(), name='user-deactivate'),
    path('users/<int:pk>/activate/', views.UserActivateView.as_view(), name='user-activate'),
    
    # Statistics endpoint
    path('stats/', views.user_stats_view, name='user-stats'),
] 