from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Q
from .models import Board, Feedback, Comment, FeedbackStatusHistory, BoardInvitation


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    """
    Admin interface for Board model with comprehensive management features.
    """
    list_display = (
        'name', 'owner', 'visibility', 'feedback_count', 'total_votes',
        'is_active', 'created_at', 'moderator_count', 'member_count'
    )
    list_filter = (
        'visibility', 'is_active', 'allow_anonymous_feedback', 'require_approval',
        'allow_comments', 'allow_voting', 'created_at'
    )
    search_fields = ('name', 'description', 'slug', 'owner__email', 'owner__username')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at', 'feedback_count', 'total_votes')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'slug', 'visibility')
        }),
        ('Board Settings', {
            'fields': (
                'allow_anonymous_feedback', 'require_approval',
                'allow_comments', 'allow_voting'
            )
        }),
        ('Access Control', {
            'fields': ('owner', 'moderators', 'members'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    filter_horizontal = ('moderators', 'members')
    
    def feedback_count(self, obj):
        """Display feedback count with link."""
        count = obj.feedback_count
        url = reverse('admin:feedback_feedback_changelist') + f'?board__id__exact={obj.id}'
        return format_html('<a href="{}">{} feedback items</a>', url, count)
    feedback_count.short_description = 'Feedback Items'
    
    def total_votes(self, obj):
        """Display total votes."""
        return obj.total_votes
    total_votes.short_description = 'Total Votes'
    
    def moderator_count(self, obj):
        """Display moderator count."""
        return obj.moderators.count()
    moderator_count.short_description = 'Moderators'
    
    def member_count(self, obj):
        """Display member count."""
        return obj.members.count()
    member_count.short_description = 'Members'
    
    actions = ['activate_boards', 'deactivate_boards', 'make_public', 'make_private']
    
    def activate_boards(self, request, queryset):
        """Activate selected boards."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} boards have been activated.')
    activate_boards.short_description = "Activate selected boards"
    
    def deactivate_boards(self, request, queryset):
        """Deactivate selected boards."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} boards have been deactivated.')
    deactivate_boards.short_description = "Deactivate selected boards"
    
    def make_public(self, request, queryset):
        """Make selected boards public."""
        updated = queryset.update(visibility=Board.Visibility.PUBLIC)
        self.message_user(request, f'{updated} boards are now public.')
    make_public.short_description = "Make selected boards public"
    
    def make_private(self, request, queryset):
        """Make selected boards private."""
        updated = queryset.update(visibility=Board.Visibility.PRIVATE)
        self.message_user(request, f'{updated} boards are now private.')
    make_private.short_description = "Make selected boards private"


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    """
    Admin interface for Feedback model with status management and filtering.
    """
    list_display = (
        'title', 'board', 'author_name', 'status', 'priority', 'category',
        'vote_count', 'comment_count', 'created_at', 'is_active'
    )
    list_filter = (
        'status', 'priority', 'category', 'is_active', 'board__visibility',
        'created_at', 'updated_at'
    )
    search_fields = (
        'title', 'description', 'author__email', 'author__username',
        'anonymous_name', 'anonymous_email', 'board__name'
    )
    readonly_fields = (
        'created_at', 'updated_at', 'vote_count', 'total_votes',
        'comment_count', 'author_name', 'author_email'
    )
    list_select_related = ('board', 'author', 'assigned_to')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'board', 'category')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority', 'assigned_to')
        }),
        ('Author Information', {
            'fields': ('author', 'anonymous_name', 'anonymous_email'),
            'classes': ('collapse',)
        }),
        ('Voting', {
            'fields': ('upvotes', 'downvotes'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    filter_horizontal = ('upvotes', 'downvotes')
    
    def author_name(self, obj):
        """Display author name."""
        return obj.author_name
    author_name.short_description = 'Author'
    
    def author_email(self, obj):
        """Display author email."""
        return obj.author_email
    author_email.short_description = 'Email'
    
    def vote_count(self, obj):
        """Display vote count."""
        return obj.vote_count
    vote_count.short_description = 'Votes'
    
    def total_votes(self, obj):
        """Display total votes."""
        return obj.total_votes
    total_votes.short_description = 'Total Votes'
    
    def comment_count(self, obj):
        """Display comment count with link."""
        count = obj.comment_count
        url = reverse('admin:feedback_comment_changelist') + f'?feedback__id__exact={obj.id}'
        return format_html('<a href="{}">{} comments</a>', url, count)
    comment_count.short_description = 'Comments'
    
    actions = [
        'approve_feedback', 'mark_under_review', 'mark_planned',
        'mark_in_progress', 'mark_completed', 'mark_declined',
        'activate_feedback', 'deactivate_feedback'
    ]
    
    def approve_feedback(self, request, queryset):
        """Approve selected feedback."""
        updated = queryset.update(status=Feedback.Status.PENDING)
        self.message_user(request, f'{updated} feedback items have been approved.')
    approve_feedback.short_description = "Approve selected feedback"
    
    def mark_under_review(self, request, queryset):
        """Mark selected feedback as under review."""
        updated = queryset.update(status=Feedback.Status.UNDER_REVIEW)
        self.message_user(request, f'{updated} feedback items are now under review.')
    mark_under_review.short_description = "Mark as under review"
    
    def mark_planned(self, request, queryset):
        """Mark selected feedback as planned."""
        updated = queryset.update(status=Feedback.Status.PLANNED)
        self.message_user(request, f'{updated} feedback items are now planned.')
    mark_planned.short_description = "Mark as planned"
    
    def mark_in_progress(self, request, queryset):
        """Mark selected feedback as in progress."""
        updated = queryset.update(status=Feedback.Status.IN_PROGRESS)
        self.message_user(request, f'{updated} feedback items are now in progress.')
    mark_in_progress.short_description = "Mark as in progress"
    
    def mark_completed(self, request, queryset):
        """Mark selected feedback as completed."""
        updated = queryset.update(status=Feedback.Status.COMPLETED)
        self.message_user(request, f'{updated} feedback items have been completed.')
    mark_completed.short_description = "Mark as completed"
    
    def mark_declined(self, request, queryset):
        """Mark selected feedback as declined."""
        updated = queryset.update(status=Feedback.Status.DECLINED)
        self.message_user(request, f'{updated} feedback items have been declined.')
    mark_declined.short_description = "Mark as declined"
    
    def activate_feedback(self, request, queryset):
        """Activate selected feedback."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} feedback items have been activated.')
    activate_feedback.short_description = "Activate selected feedback"
    
    def deactivate_feedback(self, request, queryset):
        """Deactivate selected feedback."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} feedback items have been deactivated.')
    deactivate_feedback.short_description = "Deactivate selected feedback"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin interface for Comment model with nested comment support.
    """
    list_display = (
        'content_preview', 'feedback', 'author_name', 'is_reply',
        'vote_count', 'reply_count', 'created_at', 'is_active'
    )
    list_filter = (
        'is_active', 'created_at', 'updated_at', 'feedback__board__visibility'
    )
    search_fields = (
        'content', 'author__email', 'author__username',
        'anonymous_name', 'anonymous_email', 'feedback__title'
    )
    readonly_fields = (
        'created_at', 'updated_at', 'vote_count', 'reply_count',
        'author_name', 'author_email', 'is_reply'
    )
    list_select_related = ('feedback', 'author', 'parent')
    
    fieldsets = (
        ('Content', {
            'fields': ('content', 'feedback', 'parent')
        }),
        ('Author Information', {
            'fields': ('author', 'anonymous_name', 'anonymous_email'),
            'classes': ('collapse',)
        }),
        ('Voting', {
            'fields': ('upvotes', 'downvotes'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    filter_horizontal = ('upvotes', 'downvotes')
    
    def content_preview(self, obj):
        """Display content preview."""
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'
    
    def author_name(self, obj):
        """Display author name."""
        return obj.author_name
    author_name.short_description = 'Author'
    
    def author_email(self, obj):
        """Display author email."""
        return obj.author_email
    author_email.short_description = 'Email'
    
    def vote_count(self, obj):
        """Display vote count."""
        return obj.vote_count
    vote_count.short_description = 'Votes'
    
    def reply_count(self, obj):
        """Display reply count."""
        return obj.reply_count
    reply_count.short_description = 'Replies'
    
    def is_reply(self, obj):
        """Display if comment is a reply."""
        return obj.is_reply
    is_reply.boolean = True
    is_reply.short_description = 'Is Reply'
    
    actions = ['activate_comments', 'deactivate_comments']
    
    def activate_comments(self, request, queryset):
        """Activate selected comments."""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} comments have been activated.')
    activate_comments.short_description = "Activate selected comments"
    
    def deactivate_comments(self, request, queryset):
        """Deactivate selected comments."""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} comments have been deactivated.')
    deactivate_comments.short_description = "Deactivate selected comments"


@admin.register(FeedbackStatusHistory)
class FeedbackStatusHistoryAdmin(admin.ModelAdmin):
    """
    Admin interface for FeedbackStatusHistory model.
    """
    list_display = (
        'feedback', 'old_status', 'new_status', 'changed_by', 'changed_at'
    )
    list_filter = ('old_status', 'new_status', 'changed_at')
    search_fields = (
        'feedback__title', 'changed_by__email', 'changed_by__username', 'notes'
    )
    readonly_fields = ('changed_at',)
    list_select_related = ('feedback', 'changed_by')
    
    fieldsets = (
        ('Status Change', {
            'fields': ('feedback', 'old_status', 'new_status')
        }),
        ('Change Details', {
            'fields': ('changed_by', 'notes', 'changed_at')
        }),
    )
    
    def has_add_permission(self, request):
        """Disable manual addition of status history."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing of status history."""
        return False


@admin.register(BoardInvitation)
class BoardInvitationAdmin(admin.ModelAdmin):
    """
    Admin interface for BoardInvitation model.
    """
    list_display = (
        'board', 'email', 'invited_by', 'role', 'status', 'expires_at',
        'is_expired', 'created_at'
    )
    list_filter = ('status', 'role', 'created_at', 'expires_at')
    search_fields = (
        'board__name', 'email', 'invited_by__email', 'invited_by__username',
        'invited_user__email', 'invited_user__username'
    )
    readonly_fields = ('created_at', 'responded_at', 'is_expired')
    list_select_related = ('board', 'invited_by', 'invited_user')
    
    fieldsets = (
        ('Invitation Details', {
            'fields': ('board', 'email', 'invited_by', 'role')
        }),
        ('Status', {
            'fields': ('status', 'expires_at', 'responded_at')
        }),
        ('Message', {
            'fields': ('message',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def is_expired(self, obj):
        """Display if invitation is expired."""
        return obj.is_expired
    is_expired.boolean = True
    is_expired.short_description = 'Expired'
    
    actions = ['resend_invitations', 'expire_invitations']
    
    def resend_invitations(self, request, queryset):
        """Resend selected invitations."""
        # This would typically trigger email sending
        self.message_user(request, f'{queryset.count()} invitations would be resent.')
    resend_invitations.short_description = "Resend selected invitations"
    
    def expire_invitations(self, request, queryset):
        """Mark selected invitations as expired."""
        updated = queryset.update(status=BoardInvitation.Status.EXPIRED)
        self.message_user(request, f'{updated} invitations have been marked as expired.')
    expire_invitations.short_description = "Mark invitations as expired"


# Customize admin site headers for feedback management
admin.site.site_header = "Feedback Management Admin"
admin.site.site_title = "Feedback Management"
admin.site.index_title = "Feedback Management Administration"
