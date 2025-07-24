from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    """
    Custom User model with role-based access control for feedback management system.
    
    Roles:
    - Admin: Full system access and management
    - Moderator: Can manage feedback and moderate content
    - Contributor: Can submit feedback and participate in discussions
    """
    
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        MODERATOR = 'moderator', 'Moderator'
        CONTRIBUTOR = 'contributor', 'Contributor'
    
    email = models.EmailField(
        unique=True,
        help_text="Email address used for login and notifications"
    )
    
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CONTRIBUTOR,
        help_text="User role determining system permissions"
    )
    
    first_name = models.CharField(
        max_length=150,
        help_text="User's first name"
    )
    
    last_name = models.CharField(
        max_length=150,
        help_text="User's last name"
    )
    
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        help_text="User profile picture"
    )
    
    bio = models.TextField(
        max_length=500,
        blank=True,
        help_text="Brief user biography"
    )
    
    phone_number = models.CharField(
        max_length=17,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
            )
        ],
        help_text="Contact phone number"
    )
    
    company = models.CharField(
        max_length=255,
        blank=True,
        help_text="Company or organization"
    )
    
    job_title = models.CharField(
        max_length=255,
        blank=True,
        help_text="Job title or position"
    )
    
    is_email_verified = models.BooleanField(
        default=False,
        help_text="Whether the user's email address has been verified"
    )
    
    email_notifications = models.BooleanField(
        default=True,
        help_text="Whether to receive email notifications"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Use email as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        db_table = 'accounts_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"
    
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name
    
    @property
    def is_admin(self):
        """Check if user has admin role."""
        return self.role == self.Role.ADMIN
    
    @property
    def is_moderator(self):
        """Check if user has moderator role."""
        return self.role == self.Role.MODERATOR
    
    @property
    def is_contributor(self):
        """Check if user has contributor role."""
        return self.role == self.Role.CONTRIBUTOR
    
    @property
    def can_moderate(self):
        """Check if user can moderate content (admin or moderator)."""
        return self.role in [self.Role.ADMIN, self.Role.MODERATOR]
    
    @property
    def can_admin(self):
        """Check if user has admin privileges."""
        return self.role == self.Role.ADMIN
    
    def has_module_perms(self, app_label):
        """
        Return True if the user has any permissions in the given app label.
        """
        return self.is_active and (self.is_superuser or self.is_admin)
    
    def has_perm(self, perm, obj=None):
        """
        Return True if the user has the specified permission.
        """
        return self.is_active and (self.is_superuser or self.is_admin)
