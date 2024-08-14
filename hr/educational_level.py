from django.core.exceptions import ObjectDoesNotExist
from users.models import CustomUser, FurtherStudies, EducationalLevel


def get_user_highest_educational_level(user_id):
    try:
        # Fetch the user instance
        user = CustomUser.objects.get(pk=user_id)
    except CustomUser.DoesNotExist:
        raise ObjectDoesNotExist("User not found")

    # Fetch further studies for the user
    further_studies = FurtherStudies.objects.filter(user=user)

    # Check if the user has any further studies
    if not further_studies.exists():
        return None  # No further studies found

    # Get the highest educational level from further studies
    highest_educational_level = further_studies.order_by(
        '-certifications__index').first()

    # Return the highest educational level instance
    return highest_educational_level.certifications if highest_educational_level else None
