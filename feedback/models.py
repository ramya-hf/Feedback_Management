from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
import uuid

User = get_user_model()


class Board(models.Model):
    """
    Board model for organizing feedback items.
    Supports public/private boards with role-based access control.
    """
    
    class Visibility(models.TextChoices):
        PUBLIC = 'public', 'Public'
        PRIVATE = 'private', 'Private'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, help_text="Board name")
    description = models.TextField(blank=True, help_text="Board description")
    slug = models.SlugField(max_length=255, unique=True, help_text="URL-friendly identifier")
    
    visibility = models.CharField(
        max_length=10,
        choices=Visibility.choices,
        default=Visibility.PUBLIC,
        help_text="Board visibility setting"
    )
    
    # Board settings
    allow_anonymous_feedback = models.BooleanField(
        default=False,
        help_text="Allow users to submit feedback without logging in"
    )
    require_approval = models.BooleanField(
        default=False,
        help_text="Require moderator approval for new feedback"
    )
    allow_comments = models.BooleanField(
        default=True,
        help_text="Allow comments on feedback items"
    )
    allow_voting = models.BooleanField(
        default=True,
        help_text="Allow voting on feedback items"
    )
    
    # Relationships
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_boards',
        help_text="Board owner"
    )
    moderators = models.ManyToManyField(
        User,
        related_name='moderated_boards',
        blank=True,
        help_text="Users who can moderate this board"
    )
    members = models.ManyToManyField(
        User,
        related_name='member_boards',
        blank=True,
        help_text="Users with access to private boards"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, help_text="Whether the board is active")
    
    class Meta:
        db_table = 'feedback_board'
        verbose_name = 'Board'
        verbose_name_plural = 'Boards'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['visibility']),
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
            models.Index(fields=['slug']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_visibility_display()})"
    
    def get_absolute_url(self):
        """Return the URL for the board."""
        return reverse('feedback:board-detail', kwargs={'slug': self.slug})
    
    def can_access(self, user):
        """Check if user can access this board."""
        if not self.is_active:
            return False
        
        if self.visibility == self.Visibility.PUBLIC:
            return True
        
        if not user.is_authenticated:
            return False
        
        return (user == self.owner or 
                user in self.moderators.all() or 
                user in self.members.all() or
                user.is_admin)
    
    def can_moderate(self, user):
        """Check if user can moderate this board."""
        if not user.is_authenticated:
            return False
        
        return (user == self.owner or 
                user in self.moderators.all() or
                user.is_admin)
    
    def can_edit(self, user):
        """Check if user can edit this board."""
        if not user.is_authenticated:
            return False
        
        return (user == self.owner or user.is_admin)
    
    @property
    def feedback_count(self):
        """Return the number of feedback items on this board."""
        return self.feedback_items.filter(is_active=True).count()
    
    @property
    def total_votes(self):
        """Return the total votes across all feedback items."""
        return sum(item.vote_count for item in self.feedback_items.filter(is_active=True))


class Feedback(models.Model):
    """
    Feedback model representing user feedback items.
    Supports status workflow, voting, and categorization.
    """
    
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PENDING = 'pending', 'Pending Review'
        UNDER_REVIEW = 'under_review', 'Under Review'
        PLANNED = 'planned', 'Planned'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        DECLINED = 'declined', 'Declined'
        DUPLICATE = 'duplicate', 'Duplicate'
    
    class Priority(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
        CRITICAL = 'critical', 'Critical'
    
    class Category(models.TextChoices):
        FEATURE = 'feature', 'Feature Request'
        BUG = 'bug', 'Bug Report'
        IMPROVEMENT = 'improvement', 'Improvement'
        QUESTION = 'question', 'Question'
        OTHER = 'other', 'Other'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, help_text="Feedback title")
    description = models.TextField(help_text="Detailed feedback description")
    
    # Status and categorization
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        help_text="Current status of the feedback"
    )
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        help_text="Priority level"
    )
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.FEATURE,
        help_text="Feedback category"
    )
    
    # Relationships
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name='feedback_items',
        help_text="Board this feedback belongs to"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='authored_feedback',
        help_text="Feedback author (null for anonymous)"
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_feedback',
        help_text="User assigned to handle this feedback"
    )
    
    # Voting and engagement
    upvotes = models.ManyToManyField(
        User,
        related_name='upvoted_feedback',
        blank=True,
        help_text="Users who upvoted this feedback"
    )
    downvotes = models.ManyToManyField(
        User,
        related_name='downvoted_feedback',
        blank=True,
        help_text="Users who downvoted this feedback"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, help_text="Whether the feedback is active")
    
    # Anonymous feedback support
    anonymous_email = models.EmailField(
        blank=True,
        help_text="Email for anonymous feedback (optional)"
    )
    anonymous_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Name for anonymous feedback (optional)"
    )
    
    class Meta:
        db_table = 'feedback_feedback'
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedback'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
            models.Index(fields=['board', 'status']),
            models.Index(fields=['author', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
    
    def get_absolute_url(self):
        """Return the URL for the feedback item."""
        return reverse('feedback:feedback-detail', kwargs={'pk': self.pk})
    
    @property
    def vote_count(self):
        """Calculate the net vote count."""
        return self.upvotes.count() - self.downvotes.count()
    
    @property
    def total_votes(self):
        """Calculate the total number of votes."""
        return self.upvotes.count() + self.downvotes.count()
    
    @property
    def comment_count(self):
        """Return the number of comments on this feedback."""
        return self.comments.filter(is_active=True).count()
    
    @property
    def author_name(self):
        """Return the author name (user or anonymous)."""
        if self.author:
            return self.author.get_full_name() or self.author.username
        return self.anonymous_name or "Anonymous"
    
    @property
    def author_email(self):
        """Return the author email (user or anonymous)."""
        if self.author:
            return self.author.email
        return self.anonymous_email
    
    def can_vote(self, user):
        """Check if user can vote on this feedback."""
        if not user.is_authenticated:
            return False
        
        if not self.board.allow_voting:
            return False
        
        if not self.is_active:
            return False
        
        return True
    
    def can_edit(self, user):
        """Check if user can edit this feedback."""
        if not user.is_authenticated:
            return False
        
        if user.is_admin:
            return True
        
        if user == self.author:
            return True
        
        return self.board.can_moderate(user)
    
    def can_delete(self, user):
        """Check if user can delete this feedback."""
        if not user.is_authenticated:
            return False
        
        if user.is_admin:
            return True
        
        if user == self.author:
            return True
        
        return self.board.can_moderate(user)
    
    def add_vote(self, user, vote_type):
        """Add a vote to this feedback."""
        if not self.can_vote(user):
            return False
        
        if vote_type == 'upvote':
            self.upvotes.add(user)
            self.downvotes.remove(user)
        elif vote_type == 'downvote':
            self.downvotes.add(user)
            self.upvotes.remove(user)
        else:
            return False
        
        return True
    
    def remove_vote(self, user):
        """Remove user's vote from this feedback."""
        self.upvotes.remove(user)
        self.downvotes.remove(user)


class Comment(models.Model):
    """
    Comment model for feedback discussions.
    Supports nested comments and rich text.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.TextField(help_text="Comment content")
    
    # Relationships
    feedback = models.ForeignKey(
        Feedback,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text="Feedback item this comment belongs to"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='authored_comments',
        help_text="Comment author (null for anonymous)"
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        help_text="Parent comment for nested replies"
    )
    
    # Voting
    upvotes = models.ManyToManyField(
        User,
        related_name='upvoted_comments',
        blank=True,
        help_text="Users who upvoted this comment"
    )
    downvotes = models.ManyToManyField(
        User,
        related_name='downvoted_comments',
        blank=True,
        help_text="Users who downvoted this comment"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, help_text="Whether the comment is active")
    
    # Anonymous comment support
    anonymous_email = models.EmailField(
        blank=True,
        help_text="Email for anonymous comments (optional)"
    )
    anonymous_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Name for anonymous comments (optional)"
    )
    
    class Meta:
        db_table = 'feedback_comment'
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
            models.Index(fields=['feedback', 'created_at']),
            models.Index(fields=['parent', 'created_at']),
            models.Index(fields=['author', 'created_at']),
        ]
    
    def __str__(self):
        return f"Comment by {self.author_name} on {self.feedback.title[:50]}"
    
    @property
    def vote_count(self):
        """Calculate the net vote count."""
        return self.upvotes.count() - self.downvotes.count()
    
    @property
    def author_name(self):
        """Return the author name (user or anonymous)."""
        if self.author:
            return self.author.get_full_name() or self.author.username
        return self.anonymous_name or "Anonymous"
    
    @property
    def author_email(self):
        """Return the author email (user or anonymous)."""
        if self.author:
            return self.author.email
        return self.anonymous_email
    
    @property
    def is_reply(self):
        """Check if this comment is a reply to another comment."""
        return self.parent is not None
    
    @property
    def reply_count(self):
        """Return the number of replies to this comment."""
        return self.replies.filter(is_active=True).count()
    
    def can_edit(self, user):
        """Check if user can edit this comment."""
        if not user.is_authenticated:
            return False
        
        if user.is_admin:
            return True
        
        if user == self.author:
            return True
        
        return self.feedback.board.can_moderate(user)
    
    def can_delete(self, user):
        """Check if user can delete this comment."""
        if not user.is_authenticated:
            return False
        
        if user.is_admin:
            return True
        
        if user == self.author:
            return True
        
        return self.feedback.board.can_moderate(user)
    
    def can_vote(self, user):
        """Check if user can vote on this comment."""
        if not user.is_authenticated:
            return False
        
        if not self.feedback.board.allow_voting:
            return False
        
        if not self.is_active:
            return False
        
        return True


class FeedbackStatusHistory(models.Model):
    """
    Track status changes for feedback items.
    Provides audit trail for feedback lifecycle.
    """
    
    feedback = models.ForeignKey(
        Feedback,
        on_delete=models.CASCADE,
        related_name='status_history',
        help_text="Feedback item"
    )
    old_status = models.CharField(
        max_length=20,
        choices=Feedback.Status.choices,
        null=True,
        blank=True,
        help_text="Previous status"
    )
    new_status = models.CharField(
        max_length=20,
        choices=Feedback.Status.choices,
        help_text="New status"
    )
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='status_changes',
        help_text="User who made the status change"
    )
    notes = models.TextField(
        blank=True,
        help_text="Optional notes about the status change"
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'feedback_status_history'
        verbose_name = 'Status History'
        verbose_name_plural = 'Status History'
        ordering = ['-changed_at']
        indexes = [
            models.Index(fields=['feedback', 'changed_at']),
            models.Index(fields=['changed_by', 'changed_at']),
        ]
    
    def __str__(self):
        return f"{self.feedback.title}: {self.old_status} → {self.new_status}"


class BoardInvitation(models.Model):
    """
    Model for managing board invitations.
    Allows board owners to invite users to private boards.
    """
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACCEPTED = 'accepted', 'Accepted'
        DECLINED = 'declined', 'Declined'
        EXPIRED = 'expired', 'Expired'
    
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name='invitations',
        help_text="Board being invited to"
    )
    email = models.EmailField(help_text="Email address of the invitee")
    invited_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_invitations',
        help_text="User who sent the invitation"
    )
    invited_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='received_invitations',
        help_text="User who received the invitation (if registered)"
    )
    role = models.CharField(
        max_length=20,
        choices=[
            ('member', 'Member'),
            ('moderator', 'Moderator'),
        ],
        default='member',
        help_text="Role to assign to the invited user"
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        help_text="Invitation status"
    )
    message = models.TextField(
        blank=True,
        help_text="Optional message with the invitation"
    )
    expires_at = models.DateTimeField(help_text="When the invitation expires")
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'feedback_board_invitation'
        verbose_name = 'Board Invitation'
        verbose_name_plural = 'Board Invitations'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'status']),
            models.Index(fields=['board', 'status']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"Invitation to {self.board.name} for {self.email}"
    
    @property
    def is_expired(self):
        """Check if the invitation has expired."""
        return timezone.now() > self.expires_at
    
    def accept(self, user):
        """Accept the invitation."""
        if self.status != self.Status.PENDING or self.is_expired:
            return False
        
        if self.role == 'moderator':
            self.board.moderators.add(user)
        else:
            self.board.members.add(user)
        
        self.status = self.Status.ACCEPTED
        self.responded_at = timezone.now()
        self.save()
        
        return True
    
    def decline(self, user):
        """Decline the invitation."""
        if self.status != self.Status.PENDING or self.is_expired:
            return False
        
        self.status = self.Status.DECLINED
        self.responded_at = timezone.now()
        self.save()
        
        return True
