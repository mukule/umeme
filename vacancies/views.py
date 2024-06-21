from django.core.exceptions import ValidationError
from .models import Application, Resume, WorkExperience, Certification
from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from .models import *
from django.db.models import Q
from users.models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import *
from django.contrib.auth.decorators import user_passes_test
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.utils.html import format_html
from .work_experience import calculate_work_experience
from .checks import *
from django.utils import timezone
from .check_qualifications import *
from .create_application import *
from .send_mail import *
import uuid


def user_has_access_level_5(user):
    return user.is_authenticated and user.access_level == 5


@login_required
def job(request, vacancy_id):
    job = get_object_or_404(Vacancy, id=vacancy_id,
                            vacancy_type='employment', published=True)

    # Get the UserAcceptedTerms instance for the logged-in user
    user_accepted_terms, created = UserAcceptedTerms.objects.get_or_create(
        user=request.user
    )

    context = {
        'vacancy': job,
        'user_accepted_terms': user_accepted_terms,
    }

    return render(request, 'vacancies/job.html', context)


def internships(request):
    search_query = request.GET.get('search')
    vacancy_type_filter = request.GET.get('vacancy_type')
    current_date = date.today()  # Get the current date

    internships = Vacancy.objects.filter(
        vacancy_type='internship',
        published=True,
        date_open__lte=current_date,  # Filter for open internships based on date
        date_close__gte=current_date,  # Filter for open internships based on date
    )

    if search_query:
        internships = internships.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if vacancy_type_filter:
        internships = internships.filter(vacancy_type=vacancy_type_filter)

    job_disciplines = JobDiscipline.objects.all()

    context = {
        'internships': internships,
        'selected_vacancy_type': vacancy_type_filter,
        'search_query': search_query,
        'job_disciplines': job_disciplines,
    }
    return render(request, 'vacancies/internships.html', context)


@login_required
def internship(request, vacancy_id):
    internship = get_object_or_404(
        Vacancy, id=vacancy_id, vacancy_type='internship', published=True)

    user_accepted_terms, created = UserAcceptedTerms.objects.get_or_create(
        user=request.user
    )
    return render(request, 'vacancies/internship.html', {'vacancy': internship, 'user_accepted_terms': user_accepted_terms})


def attachments(request):
    search_query = request.GET.get('search')
    vacancy_type_filter = request.GET.get('vacancy_type')
    current_date = date.today()  # Get the current date

    attachments = Vacancy.objects.filter(
        vacancy_type='attachment',
        published=True,
        date_open__lte=current_date,
        date_close__gte=current_date,
    )

    if search_query:
        attachments = attachments.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if vacancy_type_filter:
        attachments = attachments.filter(vacancy_type=vacancy_type_filter)

    job_disciplines = JobDiscipline.objects.all()

    context = {
        'attachments': attachments,
        'selected_vacancy_type': vacancy_type_filter,
        'search_query': search_query,
        'job_disciplines': job_disciplines,
    }
    return render(request, 'vacancies/attachments.html', context)


@login_required
def attachment(request, vacancy_id):
    attachment = get_object_or_404(
        Vacancy, id=vacancy_id, vacancy_type='attachment', published=True)

    user_accepted_terms, created = UserAcceptedTerms.objects.get_or_create(
        user=request.user
    )

    context = {
        'vacancy': attachment,
        'user_accepted_terms': user_accepted_terms,
    }
    return render(request, 'vacancies/attachment.html', context)


unique_identifier = uuid.uuid4().hex[:6]


def generate_reference_number(vacancy):
    application_count = Application.objects.filter(vacancy=vacancy).count() + 1
    return f"{vacancy.ref}/#{application_count}"


def send_application_confirmation_email(user, vacancy, reference_number):
    """
    This function sends an application confirmation email to the user.
    """

    # Construct the email subject
    mail_subject = f"Application successful for {vacancy.title}"

    full_name = f"{user.first_name} {user.last_name}"
    vacancy_details = f"{vacancy.title} ({vacancy.ref})"

    # Construct the email message
    user_message = format_html(
        "Dear {},\n\nYour application for {} has been successfully made. Only shortlisted candidates will be contacted.\n\nYour application reference number is: {}\n\nRegards,\nKenGen Careers Portal",
        full_name,
        vacancy_details,
        reference_number
    )

    # Create the email
    user_email = EmailMessage(mail_subject, user_message, to=[
                              user.email], bcc=["nelson.masibo@kenyaweb.com"])

    # Send the email
    user_email.send()


@login_required
def apply(request, vacancy_id):
    def redirect_with_error(message):
        messages.error(request, message)
        return redirect(request.META.get('HTTP_REFERER', '/'))

    vacancy = get_object_or_404(Vacancy, id=vacancy_id)
    user = request.user

    # Check if user has already applied
    if Application.objects.filter(applicant=user, vacancy=vacancy).exists():
        return redirect_with_error('You have already applied for this job.')

    # Check for basic education and resume
    if not BasicEducation.objects.filter(user=user).exists() or not Resume.objects.filter(user=user).exists():
        if user.access_level != 5:
            return redirect_with_error('Update your Basic information / academic Details to apply !!')

    # Check for required certifications
    if vacancy.certifications_required and not Certification.objects.filter(user=user).exists():
        return redirect_with_error('Certifications are required for this position')

    # Check for required college/university details
    if vacancy.college_required and not FurtherStudies.objects.filter(user=user).exists():
        return redirect_with_error('College/University Details are required for this position')

    # Check for required professional membership
    if vacancy.membership_required and not Membership.objects.filter(user=user).exists():
        return redirect_with_error('Professional Membership required for this position')

    # Check for minimum number of referees
    if Referee.objects.filter(user=user).count() < 3:
        if user.access_level != 5:
            return redirect_with_error('You don\'t have enough referees to apply. 3 referees are required.')

    user_resume = get_object_or_404(Resume, user=user)
    user_work_experience = WorkExperience.objects.filter(user=user)
    total_work_experience_years, total_work_experience_months = calculate_work_experience(
        user_work_experience)

    min_educational_level = vacancy.min_educational_level

    # Get the highest educational level
    further_studies = FurtherStudies.objects.filter(
        user=user).order_by('-certifications__index').first()
    user_educational_level = further_studies.certifications if further_studies else None

    if not user_educational_level:
        return redirect_with_error('Missing Highest Education Level, Update College/University to apply')

    # Check qualification levels
    qualify_educational_level = user_educational_level.index >= min_educational_level.index
    qualify_work_experience = (total_work_experience_years * 12 +
                               total_work_experience_months) >= vacancy.min_work_experience

    # Determine disqualification reason
    disqualification_reason = "Not Available"
    if not qualify_educational_level and not qualify_work_experience:
        disqualification_reason = "Does not meet required education level and work experience"
    elif not qualify_educational_level:
        disqualification_reason = "Does not meet required education level"
    elif not qualify_work_experience:
        disqualification_reason = "Does not have enough work experience"

    highest_educational_level = user_educational_level.name if user_educational_level else None

    # Create and save application
    application = Application(
        applicant=user,
        vacancy=vacancy,
        highest_educational_level=highest_educational_level,
        work_experience=total_work_experience_years,
        months=total_work_experience_months,
        qualify=qualify_educational_level and qualify_work_experience,
        disqualification_reason=disqualification_reason,
    )

    try:
        reference_number = generate_reference_number(vacancy)
        application.reference_number = reference_number
        application.full_clean()
        application.save()

        # Attempt to send confirmation email
        try:
            send_application_confirmation_email(
                user, vacancy, reference_number)
        except Exception as e:
            # Log the error or handle it accordingly
            messages.warning(
                request, 'Application submitted successfully, but there was an error sending the confirmation email.')

        request.session['application_id'] = application.id
        return redirect('vacancies:apply_succ')

    except ValidationError as e:
        messages.error(request, e.message_dict)
        return redirect_with_error('There was an error with your application. Please try again.')


def application_succ(request):
    # Retrieve the Application object's ID from the session
    application_id = request.session.get('application_id')

    if application_id:
        # Retrieve the Application object from the database using its ID
        application = get_object_or_404(Application, id=application_id)

        # Access the application's attributes as needed
        # Assuming you have a 'vacancy' attribute in your Application model
        vacancy_title = application.vacancy.title
        reference_number = application.reference_number

        context = {
            'vacancy_title': vacancy_title,
            'reference_number': reference_number,
        }
        return render(request, 'vacancies/apply_succ.html', context)


@login_required
def applications(request):
    user = request.user
    print(user)

    if user.access_level == 5:
        try:
            profile_update = ProfileUpdate.objects.get(user=user)
            print(profile_update)
            if not profile_update.password_changed:
                return render(request, 'main/pass_change.html')
        except ProfileUpdate.DoesNotExist:

            return render(request, 'main/pass_change.html')

    applications = Application.objects.filter(
        applicant=request.user).order_by('-application_date')
    today_date = date.today()

    context = {
        'applications': applications,
        'today_date': today_date
    }

    return render(request, 'vacancies/applications.html', context)


@login_required
def reapply_application(request, application_id):
    def redirect_with_message(message, level='error'):
        if level == 'success':
            messages.success(request, message)
        else:
            messages.error(request, message)
        return redirect(request.META.get('HTTP_REFERER', '/'))

    user = request.user
    application = get_object_or_404(Application, id=application_id)
    vacancy = application.vacancy

    # Check if the vacancy is still open
    if vacancy.date_close < timezone.now().date():
        return redirect_with_message("The application for this job is closed. You cannot edit it.")

    # Retrieve the highest educational level
    further_studies = FurtherStudies.objects.filter(
        user=user).order_by('-certifications__index').first()
    user_educational_level = further_studies.certifications if further_studies else None

    # Calculate total work experience
    user_work_experience = WorkExperience.objects.filter(user=user)
    total_work_experience_years, total_work_experience_months = calculate_work_experience(
        user_work_experience)
    total_work_experience_months_total = total_work_experience_years * \
        12 + total_work_experience_months

    min_educational_level = vacancy.min_educational_level

    # Check if the user meets the educational level requirements
    qualify_educational_level = user_educational_level.index >= min_educational_level.index if user_educational_level else False
    # Check if the user meets the work experience requirements
    qualify_work_experience = total_work_experience_months_total >= vacancy.min_work_experience

    # Determine disqualification reason
    if not qualify_educational_level and not qualify_work_experience:
        disqualification_reason = "Does not meet required education level and work experience"
    elif not qualify_educational_level:
        disqualification_reason = "Does not meet required education level"
    elif not qualify_work_experience:
        disqualification_reason = "Does not meet work experience"
    else:
        disqualification_reason = "Not Available"

    highest_educational_level = user_educational_level.name if user_educational_level else None

    # Update the application with the new information
    application.highest_educational_level = highest_educational_level
    application.work_experience = total_work_experience_years + \
        total_work_experience_months / 12
    application.qualify = qualify_educational_level and qualify_work_experience
    application.disqualification_reason = disqualification_reason
    application.years = total_work_experience_years
    application.months = total_work_experience_months

    # Save the updated application
    application.save()
    try:
        send_application_confirmation_email(
            user, vacancy, application.reference_number)
    except Exception as e:
        # Log the error or handle it accordingly
        messages.warning(
            request, 'Application submitted successfully, but there was an error sending the confirmation email.')

    return redirect_with_message('Application Re-Submitted successfully', level='success')


def redirect_to_appropriate_vacancy_page(vacancy):
    if vacancy.vacancy_type == 'Internal':
        return redirect('vacancies:internal_detail', vacancy_id=vacancy.id)
    elif vacancy.vacancy_type == 'Employment':
        return redirect('vacancies:job', vacancy_id=vacancy.id)
    elif vacancy.vacancy_type == 'Attachment':
        return redirect('vacancies:attachment', vacancy_id=vacancy.id)
    elif vacancy.vacancy_type == 'Internship':
        return redirect('vacancies:internship', vacancy_id=vacancy.id)


def delete_application(request, application_id):
    application = get_object_or_404(Application, id=application_id)

    # Get the current date
    current_date = timezone.now().date()

    # Check if the associated vacancy's end date is not greater than the current date
    if application.vacancy.date_close >= current_date:
        application.delete()
        messages.success(
            request, "Your application has been deleted successfully")
        # Redirect back to the applications page
        return redirect('vacancies:applications')
    else:
        # Display an error message using the messages framework
        messages.error(
            request, "The application for this job is closed. You cannot delete.")
        return redirect('vacancies:applications')


@user_passes_test(user_has_access_level_5)
def internal(request):
    user = request.user  # Get the logged-in user
    if user.access_level == 5:
        try:
            profile_update = ProfileUpdate.objects.get(user=user)
            if not profile_update.password_changed:
                return render(request, 'main/pass_change.html')
        except ProfileUpdate.DoesNotExist:
            return render(request, 'main/pass_change.html')
    search_query = request.GET.get('search')

    today = date.today()

    staff_vacancies = Vacancy.objects.filter(
        job_type__name='Internal',
        published=True,
        date_open__lte=today,
        date_close__gt=today
    )

    if search_query:
        staff_vacancies = staff_vacancies.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    job_disciplines = JobDiscipline.objects.all()
    internal_job_type = JobType.objects.get(name='Internal')

    context = {'jobs': staff_vacancies,
               'search_query': search_query, 'job_disciplines': job_disciplines,
               'job_type': internal_job_type,

               }
    return render(request, 'vacancies/internal.html', context)


# Apply the decorator to restrict access to the 'internal_detail' view


@login_required
@user_passes_test(user_has_access_level_5)
def internal_detail(request, vacancy_id):
    # Retrieve the specific vacancy by ID or return a 404 error if not found
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)

    user = request.user

    user_accepted_terms, created = UserAcceptedTerms.objects.get_or_create(
        user=user
    )

    context = {
        'vacancy': vacancy,
        'user_accepted_terms': user_accepted_terms,  # Include this in the context
    }
    return render(request, 'vacancies/internal_detail.html', context)


def apply_fail(request):
    return render(request, 'vacancies/apply_fail.html')
