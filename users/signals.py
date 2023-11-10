from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import CustomUser, UserAccessLog

@receiver(user_logged_in)
def log_users_with_empty_access_level(sender, request, user, **kwargs):
    if user.access_level is None:
        # Create a record of users with empty access_level
        UserAccessLog.objects.create(user=user)
