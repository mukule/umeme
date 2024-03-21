from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from users.models import *

@login_required
def resume_fields_provided(request):
    resume = request.user.resume

    required_fields = [
        'full_name', 'email_address', 'phone', 'id_number', 'dob',
        'country_of_birth', 'country_of_residence', 'ethnicity', 'religeon',
        'gender', 'disability', 'disability_number', 'marital_status',
        'educational_level', 'field_of_study'
    ]
    missing_fields = [field for field in required_fields if not getattr(resume, field)]

    if resume.country_of_residence == 'KE' and not resume.county:
        missing_fields.append('county')

    return not missing_fields

@login_required
def basic_academic_fields_provided(request):
    user = request.user

    try:
        basic_education = BasicEducation.objects.filter(user=user).first()
    except BasicEducation.DoesNotExist:
        
        return False

    
    required_fields = ['name_of_the_school', 'certification', 'date_started', 'date_ended', 'grade_attained']
    missing_fields = [field for field in required_fields if not getattr(basic_education, field)]

    
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

    
    required_fields = ['institution_name', 'certifications', 'course_undertaken', 'date_started', 'date_ended', 'grade']
    missing_fields = [field for field in required_fields if not getattr(further_studies, field)]

    
    if hasattr(further_studies, 'certificate') and not further_studies.certificate:
        missing_fields.append('certificate')

    
    return not missing_fields


@login_required
def certification_fields_provided(request):
    user = request.user

    try:
        certification = Certification.objects.filter(user=user).first()
    except Certification.DoesNotExist:
        # If certification instance doesn't exist, return False
        return False

    # Check if any required field is missing
    required_fields = ['name', 'certifying_body', 'date_attained']
    missing_fields = [field for field in required_fields if not getattr(certification, field)]

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

    # Check if any required field is missing
    required_fields = ['membership_title', 'membership_number', 'membership_body', 'date_joined']
    missing_fields = [field for field in required_fields if not getattr(membership, field)]

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
        # If work experience instance doesn't exist, return False
        return False

    # Check if any required field is missing
    required_fields = ['company_name', 'position', 'date_started', 'date_ended']
    missing_fields = [field for field in required_fields if not getattr(work_experience, field)]

    # Return True if there are no missing fields, False otherwise
    return not missing_fields



@login_required
def referee_fields_provided(request):
    user = request.user

    # Count the number of referees associated with the user
    referee_count = Referee.objects.filter(user=user).count()

    # Return False if the user has less than 3 referees
    if referee_count < 3:
        return False

    # Check if all referees have provided all required fields
    for referee in Referee.objects.filter(user=user):
        required_fields = ['full_name', 'organization', 'designation', 'phone', 'email']
        missing_fields = [field for field in required_fields if not getattr(referee, field)]
        if missing_fields:
            return False

    # If all referees have provided all required fields, return True
    return True


@login_required
def all_fields_provided(request):
    # Call each field checking function
    resume_provided = resume_fields_provided(request)
    basic_academic_provided = basic_academic_fields_provided(request)
    higher_education_provided = higher_education_fields_provided(request)
    certification_provided = certification_fields_provided(request)
    membership_provided = membership_fields_provided(request)
    experience_provided = experience_fields_provided(request)
    referee_provided = referee_fields_provided(request)

    # Check if all functions return True
    if (resume_provided and basic_academic_provided and higher_education_provided
            and certification_provided and membership_provided and experience_provided
            and referee_provided):
        return True
    else:
        return False
