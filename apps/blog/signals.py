from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Post

@receiver(pre_save, sender=Post)
def store_old_status(sender, instance, **kwargs):
    """Store the old status so post_save can detect status changes."""
    if instance.pk:
        try:
            old = Post.objects.get(pk=instance.pk)
            instance._old_status = old.status
        except Post.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Post)
def notify_on_publish(sender, instance, created, **kwargs):
    """Create a lightweight activity/notification when a post is published."""
    # Import here to avoid circular imports
    try:
        from apps.accounts.models import UserActivity
    except Exception:
        UserActivity = None

    became_published = False
    if instance.status == 'published':
        if created:
            became_published = True
        else:
            old = getattr(instance, '_old_status', None)
            if old != 'published':
                became_published = True

    if became_published and UserActivity is not None:
        # Record activity for the author
        UserActivity.objects.create(
            user=instance.author,
            activity_type='post_published',
            details={'post_id': instance.id, 'title': instance.title}
        )
