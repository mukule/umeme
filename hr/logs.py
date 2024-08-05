from users.models import Log


def create_log(user, activity):
    """
    Creates a log entry.

    :param user: User instance associated with the activity.
    :param activity: Description of the activity.
    """
    Log.objects.create(user=user, activity=activity)
