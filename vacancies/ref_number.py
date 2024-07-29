from .models import *


def generate_reference_number(vacancy):
    """
    Generate a unique reference number for an application based on the vacancy reference and the number of applications already submitted for that vacancy.

    Args:
        vacancy (Vacancy): The vacancy for which the reference number is being generated.

    Returns:
        str: The generated reference number in the format 'VAC-REF/XXX' where XXX is the count of applications plus one.
    """
    application_count = Application.objects.filter(vacancy=vacancy).count() + 1
    return f"{vacancy.ref}/#{application_count:03d}"
