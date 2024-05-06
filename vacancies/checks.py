from users.models import *


def check_basic_education_and_resume(user):
    has_basic_education = BasicEducation.objects.filter(user=user).exists()
    has_resume = Resume.objects.filter(user=user).exists()
    return has_basic_education and has_resume


def check_certifications(user, vacancy):
    if vacancy.certifications_required:
        return Certification.objects.filter(user=user).exists()
    return True


def check_college_education(user, vacancy):
    if vacancy.college_required:
        return FurtherStudies.objects.filter(user=user).exists()
    return True


def check_membership(user, vacancy):
    if vacancy.membership_required:
        return Membership.objects.filter(user=user).exists()
    return True


def check_referee_count(user):
    referee_count = Referee.objects.filter(user=user).count()
    return referee_count >= 3 or user.access_level == 5
