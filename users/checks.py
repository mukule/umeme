from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from users.models import *


@login_required
def resume_fields_provided(request):
    resume = request.user.resume

    if resume is None:
        return False

    required_fields = [
        'full_name', 'email_address', 'phone', 'id_number', 'dob',
        'country_of_birth', 'country_of_residence', 'ethnicity',
        'gender', 'disability', 'marital_status',
        'educational_level', 'field_of_study'
    ]
    missing_fields = [
        field for field in required_fields if not getattr(resume, field)]

    if resume.country_of_residence == 'KE' and not resume.county_of_birth:
        missing_fields.append('county_of_birth')

    return not missing_fields


@login_required
def basic_academic_fields_provided(request):
    user = request.user

    try:
        basic_education = BasicEducation.objects.filter(user=user).first()
    except BasicEducation.DoesNotExist:
        return False

    if basic_education is None:
        return False

    required_fields = ['name_of_the_school', 'certification',
                       'date_started', 'date_ended', 'grade_attained']
    missing_fields = [
        field for field in required_fields if not getattr(basic_education, field)]

    if hasattr(basic_education, 'certificate') and not basic_education.certificate:
        missing_fields.append('certificate')

    return not missing_fields


@login_required
def higher_education_fields_provided(request):
    user = request.user

    try:
        further_studies = FurtherStudies.objects.filter(user=user).first()
    except FurtherStudies.DoesNotExist:
        return False

    if further_studies is None:  # Add a check for None
        return False

    required_fields = ['institution_name', 'certifications',
                       'course_undertaken', 'date_started', 'date_ended', 'grade']
    missing_fields = [
        field for field in required_fields if not getattr(further_studies, field)]

    if hasattr(further_studies, 'certificate') and not further_studies.certificate:
        missing_fields.append('certificate')

    return not missing_fields


@login_required
def certification_fields_provided(request):
    user = request.user

    try:
        certification = Certification.objects.filter(user=user).first()
    except Certification.DoesNotExist:
        
        return False

    if certification is None:  
        return False

    
    required_fields = ['name', 'certifying_body', 'date_attained']
    missing_fields = [
        field for field in required_fields if not getattr(certification, field)]

    # Check if the certificate field exists and if it's missing
    if hasattr(certification, 'certificate') and not certification.certificate:
        missing_fields.append('certificate')

    # Return True if there are no missing fields, False otherwise
    return not missing_fields


@login_required
def membership_fields_provided(request):
    user = request.user

    try:
        membership = Membership.objects.filter(user=user).first()
    except Membership.DoesNotExist:
        # If membership instance doesn't exist, return False
        return False

    if membership is None:  # Add a check for None
        return False

    # Check if any required field is missing
    required_fields = ['membership_title',
                       'membership_number', 'membership_body', 'date_joined']
    missing_fields = [
        field for field in required_fields if not getattr(membership, field)]

    # Check if the certificate field exists and if it's missing
    if hasattr(membership, 'certificate') and not membership.certificate:
        missing_fields.append('certificate')

    # Return True if there are no missing fields, False otherwise
    return not missing_fields


@login_required
def experience_fields_provided(request):
    user = request.user

    try:
        work_experience = WorkExperience.objects.filter(user=user).first()
    except WorkExperience.DoesNotExist:
        # If no work experience instance exists, return False
        return False

    if work_experience is None:  # Add a check for None
        return False

    # List of required fields
    required_fields = ['company_name', 'position', 'date_started']

    # Collect missing fields
    missing_fields = [field for field in required_fields if not getattr(work_experience, field)]

    # Check if date_ended is required and missing
    if not work_experience.currently_working and not work_experience.date_ended:
        missing_fields.append('date_ended')

    # Return True if there are no missing fields, False otherwise
    return not missing_fields


@login_required
def referee_fields_provided(request):
    user = request.user

    referee_count = Referee.objects.filter(user=user).count()

    # Return False if the user has less than 3 referees
    if referee_count < 3:
        return False

    # Check if all referees have provided all required fields
    for referee in Referee.objects.filter(user=user):
        required_fields = ['full_name', 'organization',
                           'designation', 'phone', 'email']
        missing_fields = [
            field for field in required_fields if not getattr(referee, field)]
        if missing_fields:
            return False

    # If all referees have provided all required fields, return True
    return True

@login_required
def summary_provided(request):
    user = request.user

    try:
        professional_summary = ProfessionalSummary.objects.get(user=user)
    except ProfessionalSummary.DoesNotExist:
        return False

    required_fields = ['career_objective']
    missing_fields = [field for field in required_fields if not getattr(professional_summary, field)]

    return not missing_fields



@login_required
def all_fields_provided(request):
    user = request.user

    # Determine if resume or professional summary needs to be provided
    if user.access_level == 5:
        resume_provided = summary_provided(request)
    else:
        resume_provided = resume_fields_provided(request)

    # Check if all required fields are provided
    checks = [
        resume_provided,
        basic_academic_fields_provided(request),
        higher_education_fields_provided(request),
        certification_fields_provided(request),
        membership_fields_provided(request),
        experience_fields_provided(request),
        referee_fields_provided(request)
    ]

    # Return True if all checks are True, otherwise return False
    return all(checks)
