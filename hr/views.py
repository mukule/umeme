import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from users.models import *
from vacancies.models import *
from django.contrib import messages
from .forms import *
from django.db.models import Q
from excel_response import ExcelResponse
from django.http import HttpResponse
import openpyxl
from django.db.models import Count
import json
import pyperclip
from django.db.models import Q, Count
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
import openpyxl
from users.models import Staff
from users.forms import *
from django.core.paginator import *
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.core.exceptions import ValidationError
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from django.http import HttpResponseForbidden
from users.decorators import *




@admins
def dashboard(request):
    return render(request, 'hr/dashboard.html')


@login_required

def system_users(request):
    users = CustomUser.objects.filter(access_level=0)
    return render(request, 'hr/users.html', {'users': users})


@login_required

def jobs(request):
    search_query = request.GET.get('search')
    # Make sure 'job_discipline' matches the name in the template
    job_discipline_filter = request.GET.get('job_discipline')
    # Make sure 'vacancy_type' matches the name in the template
    vacancy_type_filter = request.GET.get('vacancy_type')

    jobs = Vacancy.objects.all()

    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if job_discipline_filter:
        # Ensure you filter by the correct field name ('job_discipline_id')
        jobs = jobs.filter(job_discipline_id=job_discipline_filter)

    if vacancy_type_filter:
        # Ensure you filter by the correct field name ('vacancy_type')
        jobs = jobs.filter(vacancy_type=vacancy_type_filter)

    job_disciplines = JobDiscipline.objects.all()

    context = {
        'jobs': jobs,
        'search_query': search_query,
        'selected_job_discipline': job_discipline_filter,
        'selected_vacancy_type': vacancy_type_filter,
        'job_disciplines': job_disciplines,
        'vacancy_types': Vacancy.VACANCY_TYPES,
    }

    return render(request, 'hr/jobs.html', context)


@login_required

def edit_job(request, job_id):
    job = get_object_or_404(Vacancy, pk=job_id)

    if request.method == 'POST':
        form = VacancyForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vacancy updated successfully')
            return redirect('hr:jobs')
    else:
        form = VacancyForm(instance=job)

    return render(request, 'hr/edit_job.html', {'form': form, 'job': job})


@login_required

def delete_job(request, job_id):
    job = get_object_or_404(Vacancy, pk=job_id)
    job.delete()
    messages.success(request, 'Vacancy Deleted successfully')
    return redirect('hr:jobs')


@login_required

def create_job(request):
    if request.method == 'POST':
        form = VacancyForm(request.POST)
        if form.is_valid():
            vacancy = form.save()
            messages.success(
                request, f'Vacancy "{vacancy.title}" created successfully.')
            return redirect('hr:jobs')
    else:
        form = VacancyForm()

    context = {'form': form}
    return render(request, 'hr/create_job.html', context)


@login_required
def publish(request, job_id):
    job = Vacancy.objects.get(pk=job_id)
    job.published = not job.published
    job.save()
    return redirect('hr:jobs')


@login_required
def applications(request):
    search_query = request.GET.get('search')
    job_discipline_filter = request.GET.get('job_discipline')
    vacancy_type_filter = request.GET.get('vacancy_type')
    # Retrieve all vacancies
    jobs = Vacancy.objects.all()

    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if job_discipline_filter:
        # Ensure you filter by the correct field name ('job_discipline_id')
        jobs = jobs.filter(job_discipline_id=job_discipline_filter)

    if vacancy_type_filter:
        # Ensure you filter by the correct field name ('vacancy_type')
        jobs = jobs.filter(vacancy_type=vacancy_type_filter)

    # Retrieve all applications
    applications = Application.objects.all()

    job_disciplines = JobDiscipline.objects.all()

    context = {
        'jobs': jobs,
        'applications': applications,
        'selected_vacancy_type': vacancy_type_filter,
        'search_query': search_query,
        'job_disciplines': job_disciplines,
        'vacancy_types': Vacancy.VACANCY_TYPES,
    }

    return render(request, 'hr/applications.html', context)


@login_required
def application_detail(request, vacancy_id, filter_criteria=None):
    # Retrieve the vacancy object or return a 404 if it doesn't exist
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)

    # Retrieve all applications related to this vacancy
    applications = Application.objects.filter(vacancy=vacancy)

    educational_levels = EducationalLevel.objects.all()

    # Apply filters based on the filter criteria if it's provided
    if filter_criteria:
        if filter_criteria == 'qualified':
            applications = applications.filter(qualify=True)
        elif filter_criteria == 'disqualified':
            applications = applications.filter(qualify=False)
        elif filter_criteria == 'shortlisted':
            applications = applications.filter(shortlisted=True)

    # Additional filters
    education_level = request.GET.get('education_level')
    ethnicity = request.GET.get('ethnicity')
    gender = request.GET.get('gender')
    disability = request.GET.get('disability')
    experience = request.GET.get('experience')
    name_search = request.GET.get('name_search')

    # Apply additional filters
    if education_level:
        applications = applications.filter(
            applicant__resume__educational_level=education_level)
    if ethnicity:
        applications = applications.filter(
            applicant__resume__ethnicity=ethnicity)
    if gender:
        applications = applications.filter(applicant__resume__gender=gender)
    if disability:
        applications = applications.filter(
            applicant__resume__disability=disability)
    if experience:
        applications = applications.filter(
            applicant__work_experiences__years__gte=experience)
    if name_search:
        applications = applications.filter(
            Q(applicant__first_name__icontains=name_search) |
            Q(applicant__last_name__icontains=name_search)
        )

    # Check if the user wants to export to Excel
    export_excel = request.GET.get('export_excel')
    if export_excel:
        # Create a list of dictionaries representing the data you want to export
        data = []
        for application in applications:
            user = application.applicant
            resume = user.resume
            basic_education = user.basic_education.first()
            further_studies = user.further_studies.first()
            work_experience = user.work_experiences.first()
            certifications = user.certifications.all()

            full_name = user.get_full_name()
            username = user.username  # Add this line to get the username

            application_data = {
                # Include username in the "Name" field
                'Name': f"{full_name} ({username})",
                'Date Applied': application.application_date.strftime("%Y-%m-%d %H:%M:%S"),
                'Reference Number': application.reference_number,
                'Experience': f"{application.work_experience} years",
                'Status': 'Qualified' if application.qualify else 'Not Qualified',
                'Shortlisted': 'Yes' if application.shortlisted else 'No',
                'Educational Level': resume.educational_level.name if resume.educational_level else '',
                'Ethnicity': resume.ethnicity.name if resume.ethnicity else '',
                'Gender': resume.gender if resume.gender else '',
                'Disability': 'Yes' if resume.disability else 'No',
            }

            if basic_education:
                application_data['Basic Education'] = basic_education.name_of_the_school
                application_data['Basic Education Certification'] = basic_education.certification
                application_data['Basic Education Grade'] = basic_education.grade_attained
                application_data['Basic Education Dates'] = f"{basic_education.date_started} - {basic_education.date_ended}"

            if further_studies:
                application_data['Further Studies'] = further_studies.institution_name
                application_data['Further Studies Certification'] = further_studies.certifications.certification_name
                application_data['Further Studies Course'] = further_studies.course_undertaken
                application_data['Further Studies Dates'] = f"{further_studies.date_started} - {further_studies.date_ended}"

            if work_experience:
                application_data['Company Name'] = work_experience.company_name
                application_data['Position'] = work_experience.position
                application_data['Work Experience Dates'] = f"{work_experience.date_started} - {work_experience.date_ended}"

            if certifications:
                application_data['Certifications'] = ', '.join(
                    [cert.name for cert in certifications])

            data.append(application_data)

        # Define column headers
        headers = [
            'Name', 'Date Applied', 'Reference Number', 'Experience', 'Status', 'Shortlisted',
            'Educational Level', 'Ethnicity', 'Gender', 'Disability',
            'Basic Education', 'Basic Education Certification', 'Basic Education Grade', 'Basic Education Dates',
            'Further Studies', 'Further Studies Certification', 'Further Studies Course', 'Further Studies Dates',
            'Company Name', 'Position', 'Work Experience Dates',
            'Certifications',
        ]

        # Create an HttpResponse with CSV content type for exporting
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="applications.csv"'

        # Create a CSV writer and write data to the response
        writer = csv.DictWriter(response, fieldnames=headers)
        writer.writeheader()
        for application_data in data:
            writer.writerow(application_data)

        return response

    context = {
        'vacancy': vacancy,
        'educational_levels': educational_levels,
        'applications': applications,
    }

    return render(request, 'hr/application_detail.html', context)


@login_required
def toggle_shortlist(request, vacancy_id, application_id):
    application = get_object_or_404(Application, pk=application_id)

    # Toggle the shortlisted status
    application.shortlisted = not application.shortlisted
    application.save()

    # Redirect to the application detail page for the specified vacancy_id
    return redirect('hr:application_detail', vacancy_id=vacancy_id)


@login_required
def resume(request, user_id):
    # Retrieve the user (applicant) and related information
    applicant = get_object_or_404(CustomUser, pk=user_id)

    try:
        resume = Resume.objects.get(user=applicant)
    except Resume.DoesNotExist:
        resume = None  # Set resume to None if it doesn't exist

    try:
        basic_education = BasicEducation.objects.get(user=applicant)
    except BasicEducation.DoesNotExist:
        basic_education = None  # Set basic_education to None if it doesn't exist

    try:
        further_studies = FurtherStudies.objects.get(user=applicant)
    except FurtherStudies.DoesNotExist:
        further_studies = None  # Set further_studies to None if it doesn't exist

    try:
        memberships = Membership.objects.filter(user=applicant)
    except Membership.DoesNotExist:
        memberships = []  # Set memberships to an empty list if they don't exist

    try:
        work_experiences = WorkExperience.objects.filter(user=applicant)
    except WorkExperience.DoesNotExist:
        work_experiences = []  # Set work_experiences to an empty list if they don't exist

    try:
        referees = Referee.objects.filter(user=applicant)
    except Referee.DoesNotExist:
        referees = []  # Set referees to an empty list if they don't exist

    try:
        certifications = Certification.objects.filter(user=applicant)
    except Certification.DoesNotExist:
        certifications = []  # Set certifications to an empty list if they don't exist

    try:
        objective = ProfessionalSummary.objects.get(user=applicant)
    except ProfessionalSummary.DoesNotExist:
        objective = None  # Set objective to None if it doesn't exist

    context = {
        'applicant': applicant,
        'resume': resume,
        'basic_education': basic_education,
        'further_studies': further_studies,
        'memberships': memberships,
        'work_experience': work_experiences,
        'referees': referees,
        'certifications': certifications,
        'objective': objective,
    }

    return render(request, 'hr/resume.html', context)


@login_required
def create_job_discipline(request):
    if request.method == 'POST':
        form = JobDisciplineForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Job discipline added succesfully")
            # Redirect to a success page after creating the discipline
            return redirect('hr:job_disclipines')
    else:
        form = JobDisciplineForm()

    return render(request, 'hr/create_job_discipline.html', {'form': form})


@login_required
def job_disciplines(request):
    # Retrieve all job disciplines and annotate them with the vacancy count
    job_disciplines = JobDiscipline.objects.annotate(
        vacancy_count=Count('vacancy'))

    return render(request, 'hr/job_disciplines.html', {'job_discipline': job_disciplines})


@login_required
def update_job_discipline(request, job_discipline_id):
    job_discipline = get_object_or_404(JobDiscipline, pk=job_discipline_id)

    if request.method == 'POST':
        form = JobDisciplineForm(request.POST, instance=job_discipline)
        if form.is_valid():
            form.save()
            # Redirect to the job disciplines list after updating
            return redirect('hr:job_disciplines')
    else:
        form = JobDisciplineForm(instance=job_discipline)

    return render(request, 'hr/update_job_discipline.html', {'form': form, 'job_discipline': job_discipline})


@login_required
def delete_job_discipline(request, job_discipline_id):
    job_discipline = get_object_or_404(JobDiscipline, pk=job_discipline_id)

    job_discipline.delete()
    return redirect('hr:job_disciplines')


@login_required
def create_certifying_body(request):
    if request.method == 'POST':
        form = CertifyingBodyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Certfying body added succesfully")
            return redirect('hr:certifying_bodies')
    else:
        form = CertifyingBodyForm()

    return render(request, 'hr/create_certifying_body.html', {'form': form})


@login_required
def certifying_bodies(request):
    certifying_bodies = CertifyingBody.objects.all()
    return render(request, 'hr/certifying_bodies.html', {'c_bodies': certifying_bodies})


@login_required
def edit_certifying_body(request, certifying_body_id):
    certifying_body = get_object_or_404(CertifyingBody, pk=certifying_body_id)

    if request.method == 'POST':
        form = CertifyingBodyForm(request.POST, instance=certifying_body)
        if form.is_valid():
            form.save()
            # Redirect to the certifying bodies list after updating
            return redirect('hr:certifying_bodies')
    else:
        form = CertifyingBodyForm(instance=certifying_body)

    return render(request, 'hr/edit_certifying_body.html', {'form': form, 'c_body': certifying_body})


@login_required
def delete_certifying_body(request, certifying_body_id):
    certifying_body = get_object_or_404(CertifyingBody, pk=certifying_body_id)

    certifying_body.delete()
    # Redirect to the certifying bodies list after deletion
    return redirect('hr:certifying_bodies')


@login_required
def create_certificate(request):
    if request.method == 'POST':
        form = CertificateForm(request.POST)
        if form.is_valid():
            form.save()
            # Redirect to a success page or the certificate list page
            return redirect('hr:certificates')
    else:
        form = CertificateForm()

    return render(request, 'hr/create_certificate.html', {'form': form})


@login_required
def certificates(request):
    certificates = Certificate.objects.all()
    return render(request, 'hr/certificates.html', {'certificate': certificates})


@login_required
def edit_certificate(request, certificate_id):
    # Get the certificate instance to be edited
    certificate = get_object_or_404(Certificate, pk=certificate_id)

    if request.method == 'POST':
        form = CertificateForm(request.POST, instance=certificate)
        if form.is_valid():
            form.save()
            # Redirect to the certificates list page
            return redirect('hr:certificates')
    else:
        form = CertificateForm(instance=certificate)

    return render(request, 'hr/edit_certificate.html', {'form': form, 'certificate': certificate})


@login_required
def delete_certificate(request, certificate_id):
    # Get the certificate instance to be deleted
    certificate = get_object_or_404(Certificate, pk=certificate_id)

    certificate.delete()
    # Redirect to the certificates list page
    return redirect('hr:certificates')


@login_required
def create_field_of_study(request):
    if request.method == 'POST':
        form = FieldOfStudyForm(request.POST)
        if form.is_valid():
            form.save()
            # Redirect to the list view after creating
            return redirect('hr:fields_of_study')
    else:
        form = FieldOfStudyForm()

    return render(request, 'hr/create_field_of_study.html', {'form': form})


@login_required
def edit_field_of_study(request, field_of_study_id):
    field_of_study = FieldOfStudy.objects.get(pk=field_of_study_id)

    if request.method == 'POST':
        form = FieldOfStudyForm(request.POST, instance=field_of_study)
        if form.is_valid():
            form.save()
            # Redirect to the list view after editing
            return redirect('hr:fields_of_study')
    else:
        form = FieldOfStudyForm(instance=field_of_study)

    return render(request, 'hr/edit_field_of_study.html', {'form': form})


@login_required
def delete_field_of_study(request, field_of_study_id):
    field_of_study = FieldOfStudy.objects.get(pk=field_of_study_id)

    field_of_study.delete()
    # Redirect to the list view after deleting
    return redirect('hr:fields_of_study')


@login_required
def fields_of_study(request):
    fields_of_study = FieldOfStudy.objects.all()
    return render(request, 'hr/fields_of_study.html', {'fields_of_study': fields_of_study})


@login_required
def edu_levels(request):
    edu_levels = EducationalLevel.objects.all()
    return render(request, 'hr/edu_levels.html', {'edu_levels': edu_levels})


@login_required
def create_ethnicity(request):
    if request.method == 'POST':
        form = EthnicityForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('hr:ethnicities')
    else:
        form = EthnicityForm()
    return render(request, 'hr/create_ethnicity.html', {'form': form})


@login_required
def ethnicities(request):
    ethnicities = Ethnicity.objects.all()
    return render(request, 'hr/ethnicities.html', {'ethnicities': ethnicities})


@login_required
def edit_ethnicity(request, ethnicity_id):
    ethnicity = get_object_or_404(Ethnicity, id=ethnicity_id)
    if request.method == 'POST':
        form = EthnicityForm(request.POST, instance=ethnicity)
        if form.is_valid():
            form.save()
            return redirect('hr:ethnicities')
    else:
        form = EthnicityForm(instance=ethnicity)
    return render(request, 'hr/edit_ethnicity.html', {'form': form, 'ethnicity': ethnicity})


@login_required
def delete_ethnicity(request, ethnicity_id):
    ethnicity = get_object_or_404(Ethnicity, id=ethnicity_id)

    ethnicity.delete()
    return redirect('hr:ethnicities')


@login_required
def user_access_logs(request):
    user_logs = UserAccessLog.objects.all()
    return render(request, 'hr/user_logs.html', {'user_logs': user_logs})


@login_required
def admin_access_logs(request):
    admin_logs = AdminAccessLog.objects.all()
    return render(request, 'hr/admin_logs.html', {'admin_logs': admin_logs})


@login_required
def portal_reports(request):
    # Query to count users with access level 0
    access_level_0_count = CustomUser.objects.filter(access_level=0).count()

    # Query to count users with access level 1-4
    access_level_1_to_4_count = CustomUser.objects.filter(
        access_level__range=(1, 4)).count()

    # Query to count the number of vacancies created
    vacancy_count = Vacancy.objects.count()

    # Query to count the total number of applications
    total_applications_count = Application.objects.count()

    context = {
        'r_count': access_level_0_count,
        'a_count': access_level_1_to_4_count,
        'vacancy_count': vacancy_count,
        'applications_count': total_applications_count,
    }

    print(context)

    return render(request, 'hr/portal_reports.html', context)


@login_required
def vacancy_report(request):
    # Calculate the count of open vacancies
    open_vacancy_count = Vacancy.objects.filter(
        Q(date_open__lte=timezone.now()) &
        Q(date_close__gt=timezone.now())
    ).count()

    # Calculate the count of closed vacancies
    closed_vacancy_count = Vacancy.objects.filter(
        Q(date_close__lte=timezone.now())
    ).count()

    # Use aggregation and annotation to count the vacancies for each job discipline
    job_disciplines_counts = JobDiscipline.objects.annotate(
        vacancy_count=Count('vacancy'))

    # Prepare the data as a list of dictionaries
    data = [
        {
            'name': discipline.name,
            'vacancy_count': discipline.vacancy_count,
        }
        for discipline in job_disciplines_counts
    ]

    # Convert data to a JSON string
    data_json = json.dumps(data)

    # Prepare data for the pie chart
    pie_chart_data = {
        'open_vacancy_count': open_vacancy_count,
        'closed_vacancy_count': closed_vacancy_count,
    }

    # Convert pie chart data to JSON
    pie_chart_data_json = json.dumps(pie_chart_data)

    all_vacancies = Vacancy.objects.all()

    return render(request, 'hr/v_report.html', {
        'job_disciplines_with_counts_json': data_json,
        'pie_chart_data_json': pie_chart_data_json,
        'jobs': all_vacancies
    })


@login_required
def applications_reports(request):
    # Retrieve counts
    total_applications = Application.objects.count()
    qualify_true_count = Application.objects.filter(qualify=True).count()
    shortlisted_true_count = Application.objects.filter(
        shortlisted=True).count()

    # Retrieve counts for each vacancy
    vacancies = Vacancy.objects.all()
    vacancy_counts = []

    for vacancy in vacancies:
        vacancy_count = Application.objects.filter(vacancy=vacancy).count()
        vacancy_counts.append({
            'vacancy_title': vacancy.title,
            'application_count': vacancy_count,
        })

    # Prepare data as a dictionary
    data = {
        'labels': ['Total Applications', 'Qualify True', 'Shortlisted True'],
        'data': [total_applications, qualify_true_count, shortlisted_true_count],
        'vacancy_data': vacancy_counts,
    }

    # Convert data to JSON
    data_json = json.dumps(data)

    context = {
        'data_json': data_json,  # Add the JSON data to the context
    }

    return render(request, 'hr/application_reports.html', context)


@login_required
def application_report(request, vacancy_id):
    # Retrieve the specific vacancy or return a 404 error if not found
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)

    # Retrieve counts for this specific vacancy
    total_applications = Application.objects.filter(vacancy=vacancy).count()
    qualify_true_count = Application.objects.filter(
        vacancy=vacancy, qualify=True).count()
    shortlisted_true_count = Application.objects.filter(
        vacancy=vacancy, shortlisted=True).count()

    # Prepare data for the graph as a dictionary
    graph_data = {
        'labels': ['Total Applications', 'Qualified Applicants', 'Shortlisted Applicants'],
        'data': [total_applications, qualify_true_count, shortlisted_true_count],
    }

    # Convert graph data to JSON
    graph_data_json = json.dumps(graph_data)

    context = {
        'vacancy': vacancy,
        # Add the JSON data for the graph to the context
        'graph_data_json': graph_data_json,
    }

    return render(request, 'hr/application_report.html', context)


@login_required
def adms(request):
    search_query = request.GET.get('q')
    users_with_access_5 = []

    if search_query:
        # Filter users based on search query and access level
        users_with_access_5 = CustomUser.objects.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(resume__full_name__icontains=search_query),
            access_level=5
        )

    context = {
        'search_query': search_query,
        'users_with_access_5': users_with_access_5,
    }

    return render(request, 'hr/adms.html', context)

def admin_role(request, admin_id):
    user_to_update = get_object_or_404(CustomUser, id=admin_id)

    if request.method == 'POST':
        form = UpdateFunctionForm(request.POST, instance=user_to_update)
        if form.is_valid():
            form.save()
            # Redirect to a success page or any other appropriate action
            return redirect('hr:hr_admins')  # Replace with your desired URL
    else:
        form = UpdateFunctionForm(instance=user_to_update)

    context = {
        'user_to_update': user_to_update,
        'form': form,
    }

    return render(request, 'hr/admin_role.html', context)


def hr_admin(request):
    # Filter users with access level 5 and function values 1, 2, 3, 4, or 5
    users_with_access_and_function = CustomUser.objects.filter(
        access_level=5,
        function__in=[1, 2, 3, 4, 5]
    )

    context = {
        'users_with_access_and_function': users_with_access_and_function,
    }

    return render(request, 'hr/hr.html', context)

@login_required
def admin_register(request):
    if request.method == 'POST':
        form = AdminForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Construct the login link
            current_site = get_current_site(request)
            # Assuming 'login' is the name of your login URL pattern
            login_link = reverse('users:login')

            # Compose the email message
            subject = 'Account Created Successfully'
            message = f"Hello {user.username},\n\nYour admin account has been created successfully. Here are your login details:\n\nUsername: {user.username}\nEmail: {user.email}\nPassword: {form.cleaned_data['password1']}\n\nYou can now use these details to log in to your account.\n\nLogin here: {current_site}{login_link}"

            from_email = 'nelson@kenyaweb.co.ke'  # Replace with your sender email
            to_email = user.email

            # Send the email
            send_mail(subject, message, from_email, [to_email])

            # Add a success message
            messages.success(
                request, f"{user.username}'s admin account has been created successfully, and login details have been sent to {user.email}.")

            # You can perform any additional actions here after user creation, if needed
            # Redirect to a success page or another URL
            return redirect('hr:adms')
        else:
            # Form has errors, display error messages
            messages.error(
                request, "There were errors in the form. Please correct them.")
    else:
        form = AdminForm()

    return render(request, 'hr/admin_register.html', {'form': form})


def create_terms(request):
    if request.method == 'POST':
        form = TermsForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            terms, created = Terms.objects.get_or_create(
                defaults={'text': text})
            if not created:
                terms.text = text
                terms.save()
            # Redirect to the terms page or any other page
            return redirect('main:terms')
    else:
        initial_text = Terms.objects.first()
        form = TermsForm(
            initial={'text': initial_text.text if initial_text else ''})

    return render(request, 'hr/create_terms.html', {'form': form})


def import_excel(request):
    if request.method == 'POST':
        form = ExcelImportForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']

            if not excel_file.name.endswith('.xlsx'):
                return render(request, 'error_page.html', {'message': 'File is not in .xlsx format.'})

            try:
                wb = load_workbook(excel_file)
                sheet_name = 'staff list 23.10.2023'
                sheet = wb[sheet_name]

                for row in sheet.iter_rows():
                    staff_no, name, email = [cell.value for cell in row]

                    try:
                        hashed_password = make_password(
                            staff_no)  # Hash the password

                        with transaction.atomic():
                            user = CustomUser.objects.create(
                                username=staff_no,
                                email=email,
                                access_level=5,
                                password=hashed_password  # Assign the hashed password
                            )

                            # Create or update the user's resume
                            resume, _ = Resume.objects.get_or_create(user=user)
                            resume.full_name = name
                            resume.email_address = email
                            resume.save()
                    except ValidationError:
                        return render(request, 'error_page.html', {'message': 'Error during import'})

                wb.close()  # Close the workbook

                return redirect('hr:staffs')
            except (KeyError, ValidationError):
                return render(request, 'error_page.html', {'message': 'Error during import'})

    else:
        form = ExcelImportForm()

    return render(request, 'hr/import_staffs.html', {'form': form})


def staffs(request):
    # Retrieve all staff members with access level 5
    staff_members = CustomUser.objects.filter(access_level=5)

    # Define the number of items per page
    items_per_page = 100

    # Filter staff members based on search criteria
    search_query = request.GET.get('search_query', '')
    if search_query:
        staff_members = staff_members.filter(
            Q(username__icontains=search_query) | Q(email__icontains=search_query))

    paginator = Paginator(staff_members, items_per_page)
    # Get the current page number from the request
    page = request.GET.get('page')

    staff_members = paginator.get_page(page)

    context = {
        'staff_members': staff_members,
        'search_query': search_query,
    }

    return render(request, 'hr/staffs.html', context)


def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)

    if user.access_level != 5:
        return HttpResponseForbidden("Access denied")

    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            # Redirect to the user list page after editing
            return redirect('hr:kgn_staffs')
    else:
        form = UserEditForm(instance=user)

    context = {
        'form': form,
        'user': user,
    }

    return render(request, 'hr/edit_staff.html', context)


def delete_staff(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)

    # Check if the user has access level 5
    if user.access_level != 5:
        return HttpResponseForbidden("Access denied")

    user.delete()
    # Redirect to the user list page after deleting
    return redirect('hr:kgn_staffs')


def reset_trials(request, user_id):
    # Get the admin user (you can implement admin authentication)
    # Get the user to reset trials for (or use get_object_or_404 to handle non-existent user)
    user_to_reset = get_object_or_404(CustomUser, id=user_id)

    # Reset the trials for the selected user
    user_to_reset.trials = 4  # Reset the trials to 3 or your desired value
    user_to_reset.is_restricted = False  # Unrestrict the user
    user_to_reset.save()

    # Add a success message
    messages.success(
        request, f"Trials reset successfully for {user_to_reset.username}. They can submit their staff No again.")

    # Redirect back to the admin panel or another appropriate page
    return redirect('hr:system_users')


def delete_users_with_access_level_5(request):
    if request.method == 'POST':
        # Delete users with access level 5
        CustomUser.objects.filter(access_level=5).delete()
        return redirect('hr:kgn_staffs')  # Redirect to a success page

    return render(request, 'hr/staffs.html')
