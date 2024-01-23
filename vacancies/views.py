from .models import Application, Resume, WorkExperience, Certification
from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from .models import *
from django.db.models import Q
from users.models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .forms import *
from django.contrib.auth.decorators import user_passes_test
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.utils.html import format_html


def user_has_access_level_5(user):
    return user.is_authenticated and user.access_level == 5


def jobs(request):
    search_query = request.GET.get('search')
    vacancy_type_filter = request.GET.get('vacancy_type')
    current_date = date.today()  # Get the current date

    jobs = Vacancy.objects.filter(
        vacancy_type='employment',
        published=True,
        date_open__lte=current_date,  # Filter for open jobs based on date
        date_close__gte=current_date,  # Filter for open jobs based on date
    )

    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if vacancy_type_filter:
        jobs = jobs.filter(vacancy_type=vacancy_type_filter)

    job_disciplines = JobDiscipline.objects.all()

    context = {
        'jobs': jobs,
        'selected_vacancy_type': vacancy_type_filter,
        'search_query': search_query,
        'job_disciplines': job_disciplines,
    }
    return render(request, 'vacancies/jobs.html', context)


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


@login_required
def apply(request, vacancy_id):
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)
    user = request.user

    # Check if the user has already applied for this job
    already_applied = Application.objects.filter(
        applicant=user, vacancy=vacancy).exists()

    if already_applied:
        messages.error(request, 'You have already applied for this job.')
        if vacancy.vacancy_type == 'Internal':
            return redirect('vacancies:internal_detail', vacancy_id=vacancy_id)
        elif vacancy.vacancy_type == 'Employment':
            return redirect('vacancies:job', vacancy_id=vacancy_id)
        elif vacancy.vacancy_type == 'Attachment':
            return redirect('vacancies:attachment', vacancy_id=vacancy_id)
        elif vacancy.vacancy_type == 'Internship':
            return redirect('vacancies:internship', vacancy_id=vacancy_id)

    # Check if the user has added basic education and further studies to their profile
    has_basic_education = BasicEducation.objects.filter(user=user).exists()
    has_resume = Resume.objects.filter(user=user).exists()

    if not has_basic_education or not has_resume:
        if user.access_level != 5:
            messages.error(
                request, 'Update your Basic information / academic Details to apply !!')
            if vacancy.vacancy_type == 'Internal':
                return redirect('vacancies:internal_detail', vacancy_id=vacancy_id)
            elif vacancy.vacancy_type == 'Employment':
                return redirect('vacancies:job', vacancy_id=vacancy_id)
            elif vacancy.vacancy_type == 'Attachment':
                return redirect('vacancies:attachment', vacancy_id=vacancy_id)
            elif vacancy.vacancy_type == 'Internship':
                return redirect('vacancies:internship', vacancy_id=vacancy_id)

    # Check if the vacancy requires certifications or college education
    if vacancy.certifications_required and not Certification.objects.filter(user=user).exists():
        messages.error(
            request, 'Certifications are required for this position')
        if vacancy.vacancy_type == 'Internal':
            return redirect('vacancies:internal_detail', vacancy_id=vacancy_id)
        elif vacancy.vacancy_type == 'Employment':
            return redirect('vacancies:job', vacancy_id=vacancy_id)
        elif vacancy.vacancy_type == 'Attachment':
            return redirect('vacancies:attachment', vacancy_id=vacancy_id)
        elif vacancy.vacancy_type == 'Internship':
            return redirect('vacancies:internship', vacancy_id=vacancy_id)

    if vacancy.college_required and not FurtherStudies.objects.filter(user=user).exists():
        messages.error(
            request, 'College/Further studies are required for this position')
        if vacancy.vacancy_type == 'Internal':
            return redirect('vacancies:internal_detail', vacancy_id=vacancy_id)
        elif vacancy.vacancy_type == 'Employment':
            return redirect('vacancies:job', vacancy_id=vacancy_id)
        elif vacancy.vacancy_type == 'Attachment':
            return redirect('vacancies:attachment', vacancy_id=vacancy_id)
        elif vacancy.vacancy_type == 'Internship':
            return redirect('vacancies:internship', vacancy_id=vacancy_id)

    if vacancy.membership_required and not Membership.objects.filter(user=user).exists():
        messages.error(
            request, 'Professional Membership required for this position')
        if vacancy.vacancy_type == 'Internal':
            return redirect('vacancies:internal_detail', vacancy_id=vacancy_id)
        elif vacancy.vacancy_type == 'Employment':
            return redirect('vacancies:job', vacancy_id=vacancy_id)
        elif vacancy.vacancy_type == 'Attachment':
            return redirect('vacancies:attachment', vacancy_id=vacancy_id)
        elif vacancy.vacancy_type == 'Internship':
            return redirect('vacancies:internship', vacancy_id=vacancy_id)
        
    referee_count = Referee.objects.filter(user=request.user).count()
    if referee_count < 3:
            if user.access_level != 5:
                messages.error(
                    request, 'You don\'t have enough referees to apply. 3 referees are required.')
                if vacancy.vacancy_type == 'Internal':
                    return redirect('vacancies:internal_detail', vacancy_id=vacancy_id)
                elif vacancy.vacancy_type == 'Employment':
                    return redirect('vacancies:job', vacancy_id=vacancy_id)
                elif vacancy.vacancy_type == 'Attachment':
                    return redirect('vacancies:attachment', vacancy_id=vacancy_id)
                elif vacancy.vacancy_type == 'Internship':
                    return redirect('vacancies:internship', vacancy_id=vacancy_id)
   
       
    # Get the user's resume and calculate total work experience
    user_resume = get_object_or_404(Resume, user=user)
    user_work_experience = WorkExperience.objects.filter(user=user)
    total_work_experience_years = sum(
        experience.years for experience in user_work_experience)
    total_work_experience_months = sum(
        experience.months for experience in user_work_experience)

    # Determine if the user's education level is sufficient for the vacancy
    min_educational_level = vacancy.min_educational_level
    user_educational_level = user_resume.educational_level

    # Calculate qualification based on the user's resume data and vacancy requirements
    qualify_educational_level = user_educational_level.index == min_educational_level.index
    qualify_work_experience = (total_work_experience_years * 12) + \
        total_work_experience_months >= vacancy.min_work_experience

    disqualification_reason = ""
    years, months = total_work_experience_years, total_work_experience_months

    if not qualify_educational_level and not qualify_work_experience:
        disqualification_reason = "Does not meet required education level and work experience"
    elif not qualify_educational_level:
        disqualification_reason = "Does not meet required education level"
    elif not qualify_work_experience:
        disqualification_reason = "Does not meet work experience"

    # Create the application with educational level, work experience, and qualification
    application = Application.objects.create(
        applicant=user,
        vacancy=vacancy,
        highest_educational_level=user_educational_level.name,
        work_experience=years,
        months=months,
        # Set the qualification status
        qualify=qualify_educational_level and qualify_work_experience,
        disqualification_reason=disqualification_reason,
    )

    # Update the reference_number based on the vacancy's reference number and application's index
    application.reference_number = f"{vacancy.ref}/{application.index}"
    application.save()
    mail_subject = f"Application successful for {vacancy.title}"
    user_message = format_html(
        "Thank you for applying for the {} position. Your application reference number is {}. Note that only shortlisted applicants will be Contacted.",
        vacancy.title,
        application.reference_number
    )
    user_email = EmailMessage(mail_subject, user_message, to=[user.email])
    try:
        user_email.send()
        request.session['application_id'] = application.id
        return redirect('vacancies:apply_succ')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('vacancies:apply_fail')


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
            # If no ProfileUpdate record exists, consider it as not changed.
            return render(request, 'main/pass_change.html')
    # Retrieve all applications for the logged-in user, ordered by application date
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
    user = request.user
    application = get_object_or_404(Application, id=application_id)
    vacancy = application.vacancy

    if vacancy.date_close >= timezone.now().date():
        # Check if the user has already applied for this job (excluding the current application being updated)
        already_applied = Application.objects.filter(
            applicant=request.user, vacancy=vacancy).exclude(id=application_id).exists()

        if already_applied:

            messages.error(request, 'You have already applied for this job.')
            return redirect('vacancies:applications')

        # Check if the user has added basic education and a resume to their profile
        has_basic_education = BasicEducation.objects.filter(
            user=request.user).exists()
        has_resume = Resume.objects.filter(user=request.user).exists()

        if not has_basic_education or not has_resume:
            if user.access_level != 5:
                messages.error(
                    request, 'Update your Basic information / academic Details to apply !!')
                return redirect('vacancies:applications')

        # Check if the vacancy requires certifications and whether the user has added them
        if vacancy.certifications_required and not Certification.objects.filter(user=request.user).exists():
            messages.error(
                request, 'Certifications are required for this vacancy. Please add your certifications to apply.')
            return redirect_to_appropriate_vacancy_page(vacancy)

        # Check if the vacancy requires college education and whether the user has added it
        if vacancy.college_required and not FurtherStudies.objects.filter(user=request.user).exists():
            messages.error(
                request, 'College/Further studies are required for this vacancy. Please add your further studies to apply.')
            return redirect_to_appropriate_vacancy_page(vacancy)
        
        referee_count = Referee.objects.filter(user=request.user).count()
      
        if referee_count < 3:
            if user.access_level != 5:
                messages.error(
                    request, 'You don\'t have enough referees to apply. 3 referees are required.')
                return redirect_to_appropriate_vacancy_page(vacancy)

        # Get the user's resume and calculate total work experience
        user_resume = get_object_or_404(Resume, user=request.user)
        user_work_experience = WorkExperience.objects.filter(user=request.user)
        total_work_experience_years = sum(
            experience.years for experience in user_work_experience)
        total_work_experience_months = sum(
            experience.months for experience in user_work_experience)
        total_work_experience_years_months = total_work_experience_years * \
            12 + total_work_experience_months

        # Determine if the user's education level is sufficient for the vacancy
        min_educational_level = vacancy.min_educational_level
        user_educational_level = user_resume.educational_level

        qualify_educational_level = (
            user_educational_level.index >= min_educational_level.index
            if user_educational_level is not None and min_educational_level is not None
            else False
        )

        # Calculate qualification based on the user's resume data and vacancy requirements
        qualify_work_experience = total_work_experience_years_months >= vacancy.min_work_experience

        disqualification_reason = ""

        if not qualify_educational_level and not qualify_work_experience:
            disqualification_reason = "Does not meet required education level and work experience"
        elif not qualify_educational_level:
            disqualification_reason = "Does not meet required education level"
        elif not qualify_work_experience:
            disqualification_reason = "Does not meet work experience"

        # Update the necessary fields of the application and save
        application.application_date = timezone.now()
        application.highest_educational_level = user_educational_level.name if user_educational_level is not None else None
        application.work_experience = total_work_experience_years_months / \
            12  # Convert months to years
        application.qualify = qualify_educational_level and qualify_work_experience
        application.disqualification_reason = disqualification_reason
        application.years = total_work_experience_years
        application.months = total_work_experience_months

        application.save()

        messages.success(request, 'Application resubmitted succesfully')
        return redirect_to_appropriate_vacancy_page(vacancy)
    else:
        messages.error(
            request, "The application for this job is closed. You cannot reapply.")
        return redirect('vacancies:applications')


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

    # Check if the associated vacancy's end date is not greater than the current date
    if application.vacancy.date_close >= timezone.now().date():
        application.delete()
        messages.error(
            request, "Your application has been deleted succesfully")
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
            print(profile_update)
            if not profile_update.password_changed:
                return render(request, 'main/pass_change.html')
        except ProfileUpdate.DoesNotExist:
            # If no ProfileUpdate record exists, consider it as not changed.
            return render(request, 'main/pass_change.html')
    search_query = request.GET.get('search')

    # Get the current date
    today = date.today()

    staff_vacancies = Vacancy.objects.filter(
        vacancy_type='Internal',
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

    context = {'staff_vacancies': staff_vacancies,
               'search_query': search_query, 'job_disciplines': job_disciplines}
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
