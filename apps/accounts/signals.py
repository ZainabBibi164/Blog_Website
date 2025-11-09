from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import User

@receiver(post_save, sender=User)
def assign_user_role_group(sender, instance, created, **kwargs):
    """
    Assign user to appropriate role group when user is created or role is changed
    """
    if created or instance.role not in [g.name.lower() for g in instance.groups.all()]:
        # Remove user from all role groups
        instance.groups.clear()
        
        # Get or create the role group
        role_group, _ = Group.objects.get_or_create(name=instance.role.title())
        
        # Add user to the appropriate role group
        instance.groups.add(role_group)

        # Set appropriate permissions based on role
        if instance.role == 'admin':
            instance.is_staff = True
            instance.is_superuser = True
        elif instance.role == 'author':
            instance.is_staff = True
            instance.is_superuser = False
        else:  # reader
            instance.is_staff = False
            instance.is_superuser = False
        
        instance.save()