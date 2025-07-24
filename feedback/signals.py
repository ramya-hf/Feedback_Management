from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import Feedback, FeedbackStatusHistory, Board, Comment, BoardInvitation


@receiver(pre_save, sender=Feedback)
def track_feedback_status_changes(sender, instance, **kwargs):
    """
    Track status changes for feedback items and create history records.
    """
    if instance.pk:  # Only for existing instances
        try:
            old_instance = Feedback.objects.get(pk=instance.pk)
            if old_instance.status != instance.status:
                # Status has changed, we'll create a history record in post_save
                instance._status_changed = True
                instance._old_status = old_instance.status
        except Feedback.DoesNotExist:
            pass


@receiver(post_save, sender=Feedback)
def create_status_history_record(sender, instance, created, **kwargs):
    """
    Create status history record when feedback status changes.
    """
    if hasattr(instance, '_status_changed') and instance._status_changed:
        FeedbackStatusHistory.objects.create(
            feedback=instance,
            old_status=getattr(instance, '_old_status', None),
            new_status=instance.status,
            changed_by=instance.assigned_to,  # Could be enhanced to track actual user
            notes=f"Status changed from {getattr(instance, '_old_status', 'None')} to {instance.status}"
        )
        
        # Clean up temporary attributes
        delattr(instance, '_status_changed')
        if hasattr(instance, '_old_status'):
            delattr(instance, '_old_status')


@receiver(post_save, sender=Board)
def update_board_slug(sender, instance, created, **kwargs):
    """
    Ensure board slug is unique and properly formatted.
    """
    if created and not instance.slug:
        # Generate slug from name if not provided
        from django.utils.text import slugify
        base_slug = slugify(instance.name)
        slug = base_slug
        counter = 1
        
        # Ensure slug uniqueness
        while Board.objects.filter(slug=slug).exclude(pk=instance.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        if slug != instance.slug:
            instance.slug = slug
            instance.save(update_fields=['slug'])


@receiver(pre_delete, sender=Feedback)
def cleanup_feedback_votes(sender, instance, **kwargs):
    """
    Clean up votes when feedback is deleted.
    """
    # Clear all votes
    instance.upvotes.clear()
    instance.downvotes.clear()


@receiver(pre_delete, sender=Comment)
def cleanup_comment_votes(sender, instance, **kwargs):
    """
    Clean up votes when comment is deleted.
    """
    # Clear all votes
    instance.upvotes.clear()
    instance.downvotes.clear()


@receiver(post_save, sender=Comment)
def update_feedback_comment_count(sender, instance, created, **kwargs):
    """
    Update feedback comment count when comments are added/removed.
    This is handled by the property method, but could be cached if needed.
    """
    if created:
        # Could implement caching here if comment counts become performance critical
        pass


@receiver(post_save, sender=Feedback)
def notify_board_owner(sender, instance, created, **kwargs):
    """
    Notify board owner when new feedback is created.
    This is a placeholder for future email notification implementation.
    """
    if created and instance.board.owner.email_notifications:
        # TODO: Implement email notification
        # send_feedback_notification_email(instance.board.owner, instance)
        pass


@receiver(post_save, sender=Feedback)
def notify_assigned_user(sender, instance, **kwargs):
    """
    Notify assigned user when feedback is assigned to them.
    This is a placeholder for future email notification implementation.
    """
    if (instance.assigned_to and 
        instance.assigned_to.email_notifications and
        hasattr(instance, '_assigned_changed') and 
        instance._assigned_changed):
        # TODO: Implement email notification
        # send_assignment_notification_email(instance.assigned_to, instance)
        pass


@receiver(pre_save, sender=Feedback)
def track_assignment_changes(sender, instance, **kwargs):
    """
    Track when feedback is assigned to different users.
    """
    if instance.pk:  # Only for existing instances
        try:
            old_instance = Feedback.objects.get(pk=instance.pk)
            if old_instance.assigned_to != instance.assigned_to:
                instance._assigned_changed = True
        except Feedback.DoesNotExist:
            pass


@receiver(post_save, sender=BoardInvitation)
def send_invitation_email(sender, instance, created, **kwargs):
    """
    Send invitation email when a new invitation is created.
    This is a placeholder for future email implementation.
    """
    if created:
        # TODO: Implement email sending
        # send_board_invitation_email(instance)
        pass


@receiver(post_save, sender=BoardInvitation)
def handle_invitation_response(sender, instance, **kwargs):
    """
    Handle invitation acceptance/decline actions.
    """
    if hasattr(instance, '_status_changed') and instance._status_changed:
        if instance.status == BoardInvitation.Status.ACCEPTED:
            # TODO: Send welcome email
            pass
        elif instance.status == BoardInvitation.Status.DECLINED:
            # TODO: Send decline notification
            pass


@receiver(pre_save, sender=BoardInvitation)
def track_invitation_status_changes(sender, instance, **kwargs):
    """
    Track invitation status changes.
    """
    if instance.pk:  # Only for existing instances
        try:
            old_instance = BoardInvitation.objects.get(pk=instance.pk)
            if old_instance.status != instance.status:
                instance._status_changed = True
        except BoardInvitation.DoesNotExist:
            pass 