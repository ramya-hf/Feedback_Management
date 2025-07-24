from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User admin interface with role-based management.
    """
    list_display = (
        'email', 'username', 'first_name', 'last_name', 'role',
        'is_active', 'is_email_verified', 'created_at', 'avatar_thumbnail'
    )
    list_filter = (
        'role', 'is_active', 'is_email_verified', 'email_notifications',
        'is_staff', 'is_superuser', 'created_at'
    )
    search_fields = ('email', 'username', 'first_name', 'last_name', 'company')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {
            'fields': ('email', 'username', 'password')
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'avatar', 'bio', 'phone_number')
        }),
        ('Professional Information', {
            'fields': ('company', 'job_title')
        }),
        ('Permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('is_email_verified', 'email_notifications'),
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 'password1', 'password2', 'role'),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'date_joined', 'last_login')
    
    def avatar_thumbnail(self, obj):
        """Display avatar thumbnail in admin list view."""
        if obj.avatar:
            return format_html(
                '<img src="{}" width="30" height="30" style="border-radius: 50%;" />',
                obj.avatar.url
            )
        return "No Avatar"
    avatar_thumbnail.short_description = "Avatar"
    
    def get_queryset(self, request):
        """Filter queryset based on user permissions."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        elif hasattr(request.user, 'is_admin') and request.user.is_admin:
            return qs
        else:
            # Non-admin users can only see their own profile
            return qs.filter(id=request.user.id)
    
    def has_change_permission(self, request, obj=None):
        """Control change permissions."""
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'is_admin') and request.user.is_admin:
            return True
        if obj and obj == request.user:
            return True
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Control delete permissions."""
        if request.user.is_superuser:
            return True
        if hasattr(request.user, 'is_admin') and request.user.is_admin:
            # Admins can't delete their own account
            if obj and obj == request.user:
                return False
            return True
        return False


# Customize admin site headers
admin.site.site_header = "Feedback Management Admin"
admin.site.site_title = "Feedback Management"
admin.site.index_title = "Welcome to Feedback Management Administration"
