from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    ROLES = (
        ('admin', 'Admin'),
        ('author', 'Author'),
        ('reader', 'Reader'),
    )
    
    role = models.CharField(max_length=10, choices=ROLES, default='reader')
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.username

class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50)  # e.g., 'post_created', 'comment_added'
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict)

    class Meta:
        verbose_name_plural = 'User Activities'
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.user.username} - {self.activity_type} at {self.timestamp}'

@receiver(post_save, sender='blog.Post')
def notify_post_published(sender, instance, created, **kwargs):
    if instance.status == 'published':
        UserActivity.objects.create(
            user=instance.author,
            activity_type='post_published',
            details={'post_id': instance.id, 'post_title': instance.title}
        )
