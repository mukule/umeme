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
from openpyxl.styles import Alignment
from django.http import JsonResponse
from .thanks import *
from .logs import *


@admins
def dashboard(request):
    return render(request, 'hr/dashboard.html')


@admins
def system_users(request):
    name = request.GET.get('name')
    email = request.GET.get('email')

    users = CustomUser.objects.filter(access_level=0)

    if name:
        users = users.filter(
            Q(username__icontains=name) |
            Q(first_name__icontains=name) |
            Q(last_name__icontains=name)
        )
    if email:
        users = users.filter(email__icontains=email)

    return render(request, 'hr/users.html', {'users': users})


@admins
def job_types(request):
    job_types_list = JobType.objects.all()
    return render(request, 'hr/job_types.html', {'job_types': job_types_list})


@admins
def create_job_type(request):
    if request.method == 'POST':
        form = JobTypeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            create_log(request.user, "Added Job Type")
            return redirect('hr:job_types')
    else:
        form = JobTypeForm()

    return render(request, 'hr/create_job_type.html', {'form': form})


@admins
def edit_job_type(request, job_type_id):
    job_type = get_object_or_404(JobType, id=job_type_id)

    if request.method == 'POST':
        form = JobTypeForm(request.POST, request.FILES, instance=job_type)
        if form.is_valid():
            form.save()
            create_log(request.user, "Edited Job Type")
            messages.success(request, 'Job Type updated successfully')
            return redirect('hr:job_types')
    else:
        form = JobTypeForm(instance=job_type)

    return render(request, 'hr/create_job_type.html', {'form': form, 'job_type': job_type})


@admins
def delete_job_type(request, job_type_id):
    job_type = get_object_or_404(JobType, id=job_type_id)

    job_type.delete()
    create_log(request.user, "Deleted job Type")
    return redirect('hr:job_types')


@admins
def create_educational_level(request):
    if request.method == 'POST':
        form = EducationalLevelForm(request.POST)
        if form.is_valid():
            form.save()
            create_log(request.user, "Added Educational Level")
            messages.success(request, 'Education Level Added Succesfully')
            return redirect('hr:edu_levels')
    else:
        form = EducationalLevelForm()
    return render(request, 'hr/create_edu_level.html', {'form': form})


@admins
def edit_educational_level(request, pk):
    educational_level = get_object_or_404(EducationalLevel, pk=pk)
    if request.method == 'POST':
        form = EducationalLevelForm(request.POST, instance=educational_level)
        if form.is_valid():
            form.save()
            create_log(request.user, "Edited Edited Educational Level")
            messages.success(request, 'Education Level Updated Succesfully')
            return redirect('educational_levels')
    else:
        form = EducationalLevelForm(instance=educational_level)
    return render(request, 'hr/create_edu_level.html', {'form': form, 'edu_lvl': educational_level})


@admins
def jobs(request):
    search_query = request.GET.get('search')
    job_discipline_filter = request.GET.get('job_discipline')
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
        # Ensure you filter by the correct field name ('job_type_id')
        jobs = jobs.filter(job_type_id=vacancy_type_filter)

    job_disciplines = JobDiscipline.objects.all()

    # Include JobTypes for 'vacancies' context variable
    vacancy_types = JobType.objects.all()

    context = {
        'jobs': jobs,
        'search_query': search_query,
        'selected_job_discipline': job_discipline_filter,
        'selected_vacancy_type': vacancy_type_filter,
        'job_disciplines': job_disciplines,
        'vacancy_types': vacancy_types,
    }

    return render(request, 'hr/jobs.html', context)


@admins
def edit_job(request, job_id):
    job = get_object_or_404(Vacancy, pk=job_id)
    user = request.user
    job_type = job.job_type.name

    # Determine user permissions
    is_superuser = user.is_superuser
    is_ict = user.function == 10 or is_superuser
    is_hradmin = user.function == 1 or is_ict
    is_edit1 = user.function == 6
    is_edit2 = user.function == 7

    is_hreditjobs = is_hradmin or is_edit1
    is_hreditinterns = is_hradmin or is_edit2

    can_edit = (
        (job_type in ['Careers', 'Internal'] and is_hreditjobs) or
        (job_type in ['Internship', 'Industrial Attachment']
         and is_hreditinterns)
    )

    if not can_edit:
        messages.error(
            request, "You do not have permission to Complete this Action")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    if request.method == 'POST':
        form = VacancyForm(request.POST, instance=job)
        if form.is_valid():
            job.last_updated_by = f'{user.first_name} {user.last_name}' if user.first_name and user.last_name else user.username
            form.save()
            create_log(request.user, "Edited Job")
            messages.success(request, 'Vacancy updated successfully')
            return redirect('hr:jobs')
        else:
            # Add error messages for invalid form data
            messages.error(
                request, 'Error updating vacancy. Please correct the errors below.')
    else:
        form = VacancyForm(instance=job)

    return render(request, 'hr/create_job.html', {'form': form, 'job': job})


@admins
def delete_job(request, job_id):
    job = get_object_or_404(Vacancy, pk=job_id)

    user = request.user
    job_type = job.job_type.name

    is_superuser = user.is_superuser
    is_ict = user.function == 10 or is_superuser
    is_hradmin = user.function == 1 or is_ict
    is_del1 = user.function == 8
    is_del2 = user.function == 9

    is_hrdeljobs = is_hradmin or is_del1
    is_hrdelinterns = is_hradmin or is_del2

    can_del = (
        (job_type in ['Careers', 'Internal'] and is_hrdeljobs) or
        (job_type in ['Internship', 'Industrial Attachment']
         and is_hrdelinterns)
    )

    if can_del:
        job.delete()
        create_log(request.user, "Deleted Job")
        messages.success(
            request, f'Vacancy {job.title} has been Deleted sucessfully')
        return redirect('hr:jobs')
    else:
        messages.error(
            request, 'You do not have permission to Complete this Action')
        return redirect(request.META.get('HTTP_REFERER', '/'))


@admins
def create_job(request):
    user = request.user

    is_superuser = user.is_superuser
    is_ict = user.function == 10 or is_superuser
    is_hradmin = user.function == 1 or is_ict
    is_post1 = user.function == 2
    is_post2 = user.function == 3

    can_create_jobs = is_hradmin or is_post1
    can_create_internships = is_hradmin or is_post2

    if request.method == 'POST':
        form = VacancyForm(request.POST)
        if form.is_valid():
            vacancy = form.save(commit=False)
            job_type = vacancy.job_type.name

            if (job_type in ['Careers', 'Internal'] and not can_create_jobs) or \
               (job_type in ['Internship', 'Industrial Attachment'] and not can_create_internships):
                messages.error(
                    request, "You do not have permission to create this type of Vacancy.")
                return redirect(request.META.get('HTTP_REFERER', '/'))

            vacancy.created_by = f'{user.first_name} {user.last_name}' if user.first_name and user.last_name else user.username
            vacancy.save()
            create_log(request.user, "Added Job")
            messages.success(
                request, f'Vacancy "{vacancy.title}" created successfully.')
            return redirect('hr:jobs')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error in {field}: {error}')
    else:
        form = VacancyForm()

    context = {'form': form}
    return render(request, 'hr/create_job.html', context)


@admins
def job_detail(request, vacancy_id):
    job = get_object_or_404(Vacancy, pk=vacancy_id)

    context = {'job': job}
    return render(request, 'hr/job_detail.html', context)


@admins
def publish(request, job_id):
    job = get_object_or_404(Vacancy, pk=job_id)
    user = request.user
    job_type = job.job_type.name

    is_superuser = user.is_superuser
    is_ict = user.function == 10 or is_superuser
    is_hradmin = user.function == 1 or is_ict
    is_pub1 = user.function == 4
    is_pub2 = user.function == 5

    is_hrpostjobs = is_hradmin or is_pub1
    is_hrpostinterns = is_hradmin or is_pub2

    can_publish = (
        (job_type in ['Careers', 'Internal'] and is_hrpostjobs) or
        (job_type in ['Internship', 'Industrial Attachment']
         and is_hrpostinterns)
    )

    if can_publish:
        job.published = not job.published
        job.save()
        create_log(request.user, "Publish/Unpublish Job")
        messages.success(
            request, f'Vacancy {job.title} has been {"published" if job.published else "unpublished"}.')
    else:
        messages.error(
            request, 'You do not have permission to Complete this Action')

    return redirect('hr:jobs')


@admins
def applications(request):
    search_query = request.GET.get('search')
    job_discipline_filter = request.GET.get('job_discipline')

    job_type_filter = request.GET.get('job_type')

    jobs = Vacancy.objects.all()

    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if job_discipline_filter:

        jobs = jobs.filter(job_discipline_id=job_discipline_filter)

    if job_type_filter:

        jobs = jobs.filter(job_type_id=job_type_filter)

    applications = Application.objects.all()

    job_disciplines = JobDiscipline.objects.all()

    context = {
        'jobs': jobs,
        'applications': applications,
        'selected_job_type': job_type_filter,
        'search_query': search_query,
        'job_disciplines': job_disciplines,

        'job_types': JobType.objects.all(),
    }

    return render(request, 'hr/applications.html', context)


@admins
def application_detail(request, vacancy_id, filter_criteria=None):

    vacancy = get_object_or_404(Vacancy, id=vacancy_id)

    applications = Application.objects.filter(vacancy=vacancy)

    educational_levels = EducationalLevel.objects.all()

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

    export_excel = request.GET.get('export_excel')
    if export_excel:
        # Create a list of dictionaries representing the data you want to export
        data = []
        for application in applications:
            user = application.applicant
            try:
                resume = user.resume
            except Resume.DoesNotExist:
                # Create a new Resume if it doesn't exist
                # Combine first and last name
                full_name = f"{user.first_name} {user.last_name}"
                resume = Resume.objects.create(
                    user=user,
                    full_name=full_name,
                    email_address=user.email,
                )

            basic_education = user.basic_education.first()
            further_studies = user.further_studies.first()
            work_experience = user.work_experiences.all()[:3]
            certifications = user.certifications.all()[:3]
            memberships = user.memberships.all()[:3]
            referees = user.referees.all()[:3]

            full_name = resume.full_name
            username = user.username
            contacts = f"{resume.phone}\n{resume.email_address}"

            application_data = {
                # Include username in the "Name" field
                'Username/Staff No.': username,
                'Full Name': full_name,
                'Contact Details': contacts,
                'Gender': resume.gender if resume.gender else '',
                'Disability': 'Yes' if resume.disability else 'No',
                'Ethnicity': resume.ethnicity.name if resume.ethnicity else '',
                'Highest Educational Level': resume.educational_level.name if resume.educational_level else '',
                'High School': '',
                'College/University': '',
                'Professional Certifications': '',
                'Professional Membership': '',
                'Work Experience': '',
                'Referees': '',
                'Date Applied': application.application_date.strftime("%Y-%m-%d %H:%M:%S"),
                'Reference Number': application.reference_number,
                'Status': 'Qualified' if application.qualify else 'Not Qualified',
                'Shortlisted': 'Yes' if application.shortlisted else 'No',
            }

            if basic_education:
                # Handle Academic Details data
                academic_data = ''
                institution_name = f"School: {basic_education.name_of_the_school}"
                start_year = f"Start Year: {basic_education.date_started}"
                end_year = f"End Year: {basic_education.date_ended}"
                grade = f"Grade attained: {basic_education.grade_attained}"
                academic_data += f"{institution_name}\n{start_year}\n{end_year}\n{grade}\n\n"

                application_data['High School'] = academic_data

            if further_studies:
                # Handle Further Studies data
                further_studies_data = f"Institution Name: {further_studies.institution_name}\n" \
                    f"Certification: {further_studies.certifications.name if further_studies.certifications else ''}\n" \
                    f"Course Undertaken: {further_studies.course_undertaken}\n" \
                    f"Start Date: {further_studies.date_started.strftime('%Y-%m-%d') if further_studies.date_started else ''}\n" \
                    f"End Date: {further_studies.date_ended.strftime('%Y-%m-%d') if further_studies.date_ended else ''}\n" \
                    f"Grade: {further_studies.grade}"

                application_data['College/University'] = further_studies_data

            if certifications:
                # Handle Certifications data
                certifications_data = ''
                for cert in certifications:
                    name = f"Name: {cert.name}"
                    certifying_body_name = f"Certifying Body: {cert.certifying_body.name if cert.certifying_body else ''}"
                    date_attained = f"Date Attained: {cert.date_attained.strftime('%Y-%m-%d') if cert.date_attained else ''}"

                    certifications_data += f"{name}\n{certifying_body_name}\n{date_attained}\n\n"

                application_data['Professional Certifications'] = certifications_data

            if certifications:
                # Handle Certifications data
                certifications_data = ''
                for cert in certifications:
                    name = f"Name: {cert.name}"
                    certifying_body_name = f"Certifying Body: {cert.certifying_body.name if cert.certifying_body else ''}"
                    date_attained = f"Date Attained: {cert.date_attained.strftime('%Y-%m-%d') if cert.date_attained else ''}"

                    certifications_data += f"{name}\n{certifying_body_name}\n{date_attained}\n\n"

                application_data['Professional Certifications'] = certifications_data

            if memberships:
                # Handle Memberships data
                memberships_data = ''
                for membership in memberships:
                    title = f"Membership Title: {membership.membership_title}"
                    number = f"Membership Number: {membership.membership_number}"
                    body = f"Membership Body: {membership.membership_body}"
                    joined_date = f"Date Joined: {membership.date_joined.strftime('%Y-%m-%d') if membership.date_joined else ''}"

                    memberships_data += f"{title}\n{number}\n{body}\n{joined_date}\n\n"

                application_data['Professional Membership'] = memberships_data

            if work_experience:
                # Handle Work Experience data
                work_experience_data = ''

                total_years = 0
                total_months = 0

                for experience in work_experience:
                    company_name = f"Company Name: {experience.company_name}"
                    position = f"Position: {experience.position}"
                    start_date = experience.date_started.strftime(
                        '%Y-%m-%d') if experience.date_started else ''
                    end_date = experience.date_ended.strftime(
                        '%Y-%m-%d') if experience.date_ended else 'In Progress' if experience.currently_working else ''
                    company_address = f"Company Address: {experience.company_address}"
                    company_phone = f"Company Phone: {experience.company_phone}"
                    responsibilities = f"Responsibilities: {experience.responsibilities}"

                    work_experience_data += f"{company_name}\n{position}\nStart Date: {start_date}\nEnd Date: {end_date}\n{company_address}\n{company_phone}\n{responsibilities}\n"

                    # Calculate the duration of each experience
                    if experience.date_started and experience.date_ended:
                        delta = experience.date_ended - experience.date_started
                        years_worked = delta.days // 365
                        months_worked = (delta.days % 365) // 30

                        work_experience_data += f"Years Worked: {years_worked} years\nMonths Worked: {months_worked} months\n\n"

                        # Accumulate for total
                        total_years += years_worked
                        total_months += months_worked

                    # Add space between instances
                    work_experience_data += "\n"

                total_experience = f"Total Experience: {total_years} years and {total_months} months"
                work_experience_data += total_experience

                application_data['Work Experience'] = work_experience_data

            if referees:
                # Handle Referees data
                referees_data = ''
                for referee in referees:
                    full_name = f"Full Name: {referee.full_name}"
                    organization = f"Organization: {referee.organization}"
                    designation = f"Designation: {referee.designation}"
                    phone = f"Phone: {referee.phone}"
                    email = f"Email: {referee.email}"

                    referees_data += f"{full_name}\n{organization}\n{designation}\n{phone}\n{email}\n\n"

                application_data['Referees'] = referees_data

            data.append(application_data)

        # Define column headers for Excel export
        headers = [
            'Username/Staff No.', 'Full Name', 'Contact Details', 'Gender', 'Disability', 'Ethnicity',
            'Highest Educational Level',
            'High School',
            'College/University',
            'Professional Certifications',
            'Professional Membership',
            'Work Experience',
            'Referees',
            'Date Applied', 'Reference Number', 'Status', 'Shortlisted',
        ]

        # Create a workbook and add a worksheet
        wb = openpyxl.Workbook()
        ws = wb.active

       # Write title
        title = f"{application.vacancy.title} / {application.vacancy.ref} Applications"
        title_row = ws.cell(row=1, column=8, value=title)
        title_row.alignment = Alignment(horizontal='center')
        title_row.font = openpyxl.styles.Font(size=14, bold=True)

        # Write headers
        for col_num, header in enumerate(headers, 1):
            ws.cell(row=2, column=col_num, value=header)
            # Adjust the width of columns as needed
            if header == 'Highest Educational Level':
                ws.column_dimensions[openpyxl.utils.get_column_letter(
                    col_num)].width = 20
            if header == 'High School':
                ws.column_dimensions[openpyxl.utils.get_column_letter(
                    col_num)].width = 20
            if header == 'Full Name':
                ws.column_dimensions[openpyxl.utils.get_column_letter(
                    col_num)].width = 20

            if header == 'Contact Details':
                ws.column_dimensions[openpyxl.utils.get_column_letter(
                    col_num)].width = 20

            if header == 'College/University':
                ws.column_dimensions[openpyxl.utils.get_column_letter(
                    col_num)].width = 20
            if header == 'Professional Certifications':
                ws.column_dimensions[openpyxl.utils.get_column_letter(
                    col_num)].width = 20

            if header == 'Professional Membership':
                ws.column_dimensions[openpyxl.utils.get_column_letter(
                    col_num)].width = 20

            if header == 'Work Experience':
                ws.column_dimensions[openpyxl.utils.get_column_letter(
                    col_num)].width = 20

            if header == 'Referees':
                ws.column_dimensions[openpyxl.utils.get_column_letter(
                    col_num)].width = 20

        # Write data
        for row_num, application_data in enumerate(data, 3):
            for col_num, value in enumerate(application_data.values(), 1):
                cell = ws.cell(row=row_num, column=col_num, value=value)
                # Adjust alignment and format for specific columns if needed
                if headers[col_num - 1] == 'High School':
                    cell.alignment = Alignment(wrap_text=True)

                if headers[col_num - 1] == 'College/University':
                    cell.alignment = Alignment(wrap_text=True)

                if headers[col_num - 1] == 'Professional Certifications':
                    cell.alignment = Alignment(wrap_text=True)

                if headers[col_num - 1] == 'Professional Membership':
                    cell.alignment = Alignment(wrap_text=True)

                if headers[col_num - 1] == 'Work Experience':
                    cell.alignment = Alignment(wrap_text=True)

                if headers[col_num - 1] == 'Referees':
                    cell.alignment = Alignment(wrap_text=True)

        # Create response
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="applications for {application.vacancy.title}-{application.vacancy.ref}.xlsx"'

        # Save the workbook to the response
        wb.save(response)

        return response

    context = {
        'vacancy': vacancy,
        'educational_levels': educational_levels,
        'applications': applications,
    }

    return render(request, 'hr/application_detail.html', context)


@admins
def toggle_shortlist(request, vacancy_id, application_id):
    application = get_object_or_404(Application, pk=application_id)

    application.shortlisted = not application.shortlisted
    create_log(request.user, "Shortlisted Applicant")
    application.save()

    return redirect('hr:application_detail', vacancy_id=vacancy_id)


@admins
def resume(request, user_id):

    applicant = get_object_or_404(CustomUser, pk=user_id)

    try:
        resume = Resume.objects.get(user=applicant)
    except Resume.DoesNotExist:
        resume = None

    try:
        basic_education = BasicEducation.objects.filter(user=applicant)
    except BasicEducation.DoesNotExist:
        basic_education = []

    try:
        further_studies = FurtherStudies.objects.filter(user=applicant)
    except FurtherStudies.DoesNotExist:
        further_studies = []

    try:
        memberships = Membership.objects.filter(user=applicant)
    except Membership.DoesNotExist:
        memberships = []

    try:
        work_experiences = WorkExperience.objects.filter(user=applicant)
    except WorkExperience.DoesNotExist:
        work_experiences = []

    try:
        referees = Referee.objects.filter(user=applicant)
    except Referee.DoesNotExist:
        referees = []

    try:
        certifications = Certification.objects.filter(user=applicant)
    except Certification.DoesNotExist:
        certifications = []

    try:
        objective = ProfessionalSummary.objects.get(user=applicant)
    except ProfessionalSummary.DoesNotExist:
        objective = None

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


@admins
def create_job_discipline(request):
    if request.method == 'POST':
        form = JobDisciplineForm(request.POST)
        if form.is_valid():
            form.save()
            create_log(request.user, "Added Job Discipline")
            messages.success(request, "Job discipline added succesfully")

            return redirect('hr:job_disciplines')
    else:
        form = JobDisciplineForm()

    return render(request, 'hr/create_job_discipline.html', {'form': form})


@admins
def job_disciplines(request):

    job_disciplines = JobDiscipline.objects.annotate(
        vacancy_count=Count('vacancy'))

    return render(request, 'hr/job_disciplines.html', {'job_discipline': job_disciplines})


@admins
def update_job_discipline(request, job_discipline_id):
    job_discipline = get_object_or_404(JobDiscipline, pk=job_discipline_id)

    if request.method == 'POST':
        form = JobDisciplineForm(request.POST, instance=job_discipline)
        if form.is_valid():
            form.save()
            create_log(request.user, "Updated Job Discipline")
            messages.success(request, "Job discipline Updated succesfully")
            return redirect('hr:job_disciplines')
    else:
        form = JobDisciplineForm(instance=job_discipline)

    return render(request, 'hr/create_job_discipline.html', {'form': form, 'jd': job_discipline})


@admins
def delete_job_discipline(request, job_discipline_id):
    job_discipline = get_object_or_404(JobDiscipline, pk=job_discipline_id)

    job_discipline.delete()
    create_log(request.user, "Deleted Job Discipline")
    return redirect('hr:job_disciplines')


@admins
def create_certifying_body(request):
    if request.method == 'POST':
        form = CertifyingBodyForm(request.POST)
        if form.is_valid():
            form.save()
            create_log(request.user, "Added Certifying Body")
            messages.success(request, "Certfying body added succesfully")
            return redirect('hr:certifying_bodies')
    else:
        form = CertifyingBodyForm()

    return render(request, 'hr/create_certifying_body.html', {'form': form})


@admins
def certifying_bodies(request):
    certifying_bodies = CertifyingBody.objects.all()
    return render(request, 'hr/certifying_bodies.html', {'c_bodies': certifying_bodies})


@admins
def edit_certifying_body(request, certifying_body_id):
    certifying_body = get_object_or_404(CertifyingBody, pk=certifying_body_id)

    if request.method == 'POST':
        form = CertifyingBodyForm(request.POST, instance=certifying_body)
        if form.is_valid():
            form.save()
            create_log(request.user, "Updated Certifying Body")
            messages.success(request, "Certfying body Updated succesfully")
            return redirect('hr:certifying_bodies')
    else:
        form = CertifyingBodyForm(instance=certifying_body)

    return render(request, 'hr/create_certifying_body.html', {'form': form, 'c_body': certifying_body})


@admins
def delete_certifying_body(request, certifying_body_id):
    certifying_body = get_object_or_404(CertifyingBody, pk=certifying_body_id)

    certifying_body.delete()
    create_log(request.user, "Deleted Certifying Body")
    return redirect('hr:certifying_bodies')


@admins
def create_certificate(request):
    if request.method == 'POST':
        form = CertificateForm(request.POST)
        if form.is_valid():
            form.save()
            create_log(request.user, "Added Certificate")
            messages.success(request, "Certificate Created succesfully")
            return redirect('hr:certificates')
    else:
        form = CertificateForm()

    return render(request, 'hr/create_certificate.html', {'form': form})


@admins
def certificates(request):
    certificates = Certificate.objects.all()
    return render(request, 'hr/certificates.html', {'certificate': certificates})


@admins
def edit_certificate(request, certificate_id):

    certificate = get_object_or_404(Certificate, pk=certificate_id)

    if request.method == 'POST':
        form = CertificateForm(request.POST, instance=certificate)
        if form.is_valid():
            form.save()
            create_log(request.user, "Edited Certificate")
            messages.success(request, "Certficate Updated succesfully")
            return redirect('hr:certificates')
    else:
        form = CertificateForm(instance=certificate)

    return render(request, 'hr/create_certificate.html', {'form': form, 'certificate': certificate})


@admins
def delete_certificate(request, certificate_id):

    certificate = get_object_or_404(Certificate, pk=certificate_id)

    certificate.delete()
    create_log(request.user, "Delete Certificate")
    return redirect('hr:certificates')


@admins
def create_field_of_study(request):
    if request.method == 'POST':
        form = FieldOfStudyForm(request.POST)
        if form.is_valid():
            form.save()
            create_log(request.user, "Added Field of Study")
            messages.success(request, "Field of Study Added succesfully")
            return redirect('hr:fields_of_study')
    else:
        form = FieldOfStudyForm()

    return render(request, 'hr/create_field_of_study.html', {'form': form})


@admins
def edit_field_of_study(request, field_of_study_id):
    field_of_study = FieldOfStudy.objects.get(pk=field_of_study_id)

    if request.method == 'POST':
        form = FieldOfStudyForm(request.POST, instance=field_of_study)
        if form.is_valid():
            form.save()
            create_log(request.user, "Edited Field of Study")
            messages.success(request, "Field of Study Updated succesfully")
            return redirect('hr:fields_of_study')
    else:
        form = FieldOfStudyForm(instance=field_of_study)

    return render(request, 'hr/create_field_of_study.html', {'form': form, 'fs': field_of_study})


@admins
def delete_field_of_study(request, field_of_study_id):
    field_of_study = FieldOfStudy.objects.get(pk=field_of_study_id)

    field_of_study.delete()
    create_log(request.user, "Deleted Field of Study")
    return redirect('hr:fields_of_study')


@admins
def fields_of_study(request):
    fields_of_study = FieldOfStudy.objects.all()
    return render(request, 'hr/fields_of_study.html', {'fields_of_study': fields_of_study})


@admins
def edu_levels(request):
    edu_levels = EducationalLevel.objects.all()
    return render(request, 'hr/edu_levels.html', {'edu_levels': edu_levels})


@admins
def delete_edu_level(request, edu_level_id):
    edu_level = get_object_or_404(EducationalLevel, id=edu_level_id)

    edu_level.delete()
    create_log(request.user, "Delete Education Levels")
    return redirect('hr:edu_levels')


@admins
def create_ethnicity(request):
    if request.method == 'POST':
        form = EthnicityForm(request.POST)
        if form.is_valid():
            form.save()
            create_log(request.user, "Added Ethnicity")
            messages.success(request, "Ethnicity Group Created succesfully")
            return redirect('hr:ethnicities')
    else:
        form = EthnicityForm()
    return render(request, 'hr/create_ethnicity.html', {'form': form})


@admins
def ethnicities(request):
    ethnicities = Ethnicity.objects.all()
    return render(request, 'hr/ethnicities.html', {'ethnicities': ethnicities})


@admins
def edit_ethnicity(request, ethnicity_id):
    ethnicity = get_object_or_404(Ethnicity, id=ethnicity_id)
    if request.method == 'POST':
        form = EthnicityForm(request.POST, instance=ethnicity)
        if form.is_valid():
            form.save()
            create_log(request.user, "Edited Ethicity")
            messages.success(request, "Ethnicity Group Updated succesfully")
            return redirect('hr:ethnicities')
    else:
        form = EthnicityForm(instance=ethnicity)
    return render(request, 'hr/create_ethnicity.html', {'form': form, 'ethnicity': ethnicity})


@admins
def delete_ethnicity(request, ethnicity_id):
    ethnicity = get_object_or_404(Ethnicity, id=ethnicity_id)

    ethnicity.delete()
    create_log(request.user, "Delete Ethnicity")
    return redirect('hr:ethnicities')


@admins
def user_access_logs(request):
    user_logs = UserAccessLog.objects.all().order_by('-timestamp')[:100]
    return render(request, 'hr/user_logs.html', {'user_logs': user_logs})


@admins
def admin_access_logs(request):
    admin_logs = AdminAccessLog.objects.all()
    return render(request, 'hr/admin_logs.html', {'admin_logs': admin_logs})


@admins
def portal_reports(request):

    access_level_0_count = CustomUser.objects.filter(access_level=0).count()

    access_level_1_to_4_count = CustomUser.objects.filter(
        access_level__range=(1, 4)).count()

    vacancy_count = Vacancy.objects.count()

    total_applications_count = Application.objects.count()

    context = {
        'r_count': access_level_0_count,
        'a_count': access_level_1_to_4_count,
        'vacancy_count': vacancy_count,
        'applications_count': total_applications_count,
    }

    print(context)

    return render(request, 'hr/portal_reports.html', context)


@admins
def vacancy_report(request):

    open_vacancy_count = Vacancy.objects.filter(
        Q(date_open__lte=timezone.now()) &
        Q(date_close__gt=timezone.now())
    ).count()

    closed_vacancy_count = Vacancy.objects.filter(
        Q(date_close__lte=timezone.now())
    ).count()

    job_disciplines_counts = JobDiscipline.objects.annotate(
        vacancy_count=Count('vacancy'))

    data = [
        {
            'name': discipline.name,
            'vacancy_count': discipline.vacancy_count,
        }
        for discipline in job_disciplines_counts
    ]

    data_json = json.dumps(data)

    pie_chart_data = {
        'open_vacancy_count': open_vacancy_count,
        'closed_vacancy_count': closed_vacancy_count,
    }

    pie_chart_data_json = json.dumps(pie_chart_data)

    all_vacancies = Vacancy.objects.all()

    return render(request, 'hr/v_report.html', {
        'job_disciplines_with_counts_json': data_json,
        'pie_chart_data_json': pie_chart_data_json,
        'jobs': all_vacancies
    })


@admins
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

    data = {
        'labels': ['Total Applications', 'Qualify True', 'Shortlisted True'],
        'data': [total_applications, qualify_true_count, shortlisted_true_count],
        'vacancy_data': vacancy_counts,
    }

    data_json = json.dumps(data)

    context = {
        'data_json': data_json,
    }

    return render(request, 'hr/application_reports.html', context)


@admins
def application_report(request, vacancy_id):

    vacancy = get_object_or_404(Vacancy, id=vacancy_id)

    total_applications = Application.objects.filter(vacancy=vacancy).count()
    qualify_true_count = Application.objects.filter(
        vacancy=vacancy, qualify=True).count()
    shortlisted_true_count = Application.objects.filter(
        vacancy=vacancy, shortlisted=True).count()

    graph_data = {
        'labels': ['Total Applications', 'Qualified Applicants', 'Shortlisted Applicants'],
        'data': [total_applications, qualify_true_count, shortlisted_true_count],
    }

    graph_data_json = json.dumps(graph_data)

    context = {
        'vacancy': vacancy,
        'graph_data_json': graph_data_json,
    }

    return render(request, 'hr/application_report.html', context)


@admins
def adms(request):
    search_query = request.GET.get('q')
    users_with_access_5 = []

    if search_query:

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


@admins
def admin_role(request, admin_id):
    user_to_update = get_object_or_404(CustomUser, id=admin_id)

    if request.method == 'POST':
        form = UpdateFunctionForm(request.POST, instance=user_to_update)
        if form.is_valid():
            form.save()

            return redirect('hr:hr_admins')
    else:
        form = UpdateFunctionForm(instance=user_to_update)

    context = {
        'user_to_update': user_to_update,
        'form': form,
    }

    return render(request, 'hr/admin_role.html', context)


@admins
def hr_admin(request):
    users_with_access_and_function = CustomUser.objects.filter(
        access_level=5,
        function__in=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    )

    context = {
        'users_with_access_and_function': users_with_access_and_function,
    }

    return render(request, 'hr/hr.html', context)


@admins
def admin_register(request):
    if request.method == 'POST':
        form = AdminForm(request.POST)
        if form.is_valid():
            user = form.save()
            create_log(request.user, "Added Staff")
            current_site = get_current_site(request)

            login_link = reverse('users:login')

            subject = 'Account Created Successfully'
            message = f"Hello {user.username},\n\nYour admin account has been created successfully. Here are your login details:\n\nUsername: {user.username}\nEmail: {user.email}\nPassword: {form.cleaned_data['password1']}\n\nYou can now use these details to log in to your account.\n\nLogin here: {current_site}{login_link}"

            from_email = 'nelson@kenyaweb.co.ke'
            to_email = user.email

            send_mail(subject, message, from_email, [to_email])

            messages.success(
                request, f"{user.username}'s admin account has been created successfully, and login details have been sent to {user.email}.")

            return redirect('hr:adms')
        else:

            messages.error(
                request, "There were errors in the form. Please correct them.")
    else:
        form = AdminForm()

    return render(request, 'hr/admin_register.html', {'form': form})


@admins
def create_terms(request):
    if request.method == 'POST':
        form = TermsForm(request.POST, request.FILES)
        if form.is_valid():
            text = form.cleaned_data['text']
            term_type = form.cleaned_data['term_type']
            banner = form.cleaned_data['banner']

            # Check if terms of the specified type already exist
            if Terms.objects.filter(term_type=term_type).exists():
                messages.error(
                    request, f"Terms and Conditions for {term_type.capitalize()} already exist.")
            else:
                # Create new terms with banner
                Terms.objects.create(
                    text=text,
                    term_type=term_type,
                    banner=banner
                )
                create_log(
                    request.user, f"Created {term_type.capitalize()} Terms")
                messages.success(
                    request, f"{term_type.capitalize()} Terms and Conditions created successfully.")
                return redirect('hr:terms')
    else:
        form = TermsForm()

    return render(request, 'hr/create_terms.html', {'form': form})


@admins
def terms(request):
    terms = Terms.objects.all()
    print(terms)
    return render(request, 'hr/terms.html', {'terms': terms})


@admins
def edit_terms(request, id):
    terms = get_object_or_404(Terms, id=id)

    if request.method == 'POST':
        form = TermsForm(request.POST, request.FILES, instance=terms)
        if form.is_valid():
            form.save()
            create_log(request.user, "Edited Terms")
            messages.success(
                request, "Terms and Conditions updated successfully.")
            return redirect('hr:terms')
        else:
            messages.error(
                request, "There was an error updating the Terms and Conditions. Please check the form and try again.")
    else:
        form = TermsForm(instance=terms)

    return render(request, 'hr/create_terms.html', {'form': form})


def term(request, id):
    terms = get_object_or_404(Terms, id=id)
    return render(request, 'hr/term.html', {'term': terms})


@admins
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
                            staff_no)

                        with transaction.atomic():
                            user = CustomUser.objects.create(
                                username=staff_no,
                                email=email,
                                access_level=5,
                                password=hashed_password
                            )

                            resume, _ = Resume.objects.get_or_create(user=user)
                            resume.full_name = name
                            resume.email_address = email
                            resume.save()
                    except ValidationError:
                        return render(request, 'error_page.html', {'message': 'Error during import'})

                wb.close()

                return redirect('hr:staffs')
            except (KeyError, ValidationError):
                return render(request, 'error_page.html', {'message': 'Error during import'})

    else:
        form = ExcelImportForm()

    return render(request, 'hr/import_staffs.html', {'form': form})


@admins
def staffs(request):

    staff_members = CustomUser.objects.filter(access_level=5)

    items_per_page = 100

    search_query = request.GET.get('search_query', '')
    if search_query:
        staff_members = staff_members.filter(
            Q(username__icontains=search_query) | Q(email__icontains=search_query))

    paginator = Paginator(staff_members, items_per_page)

    page = request.GET.get('page')

    staff_members = paginator.get_page(page)

    context = {
        'staff_members': staff_members,
        'search_query': search_query,
    }

    return render(request, 'hr/staffs.html', context)


@admins
def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)

    # Check if the user has access level 5
    if request.user.access_level != 5:
        return HttpResponseForbidden("Access denied")

    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            try:
                form.save()
                create_log(request.user, "Edited User")
                messages.success(request, 'User details updated successfully.')
                return redirect('hr:kgn_staffs')
            except Exception as e:
                messages.error(
                    request, f"An error occurred while updating user details: {str(e)}")
        else:

            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
    else:
        form = UserEditForm(instance=user)

    context = {
        'form': form,
        'user1': user,
    }

    return render(request, 'hr/create_staff.html', context)


@admins
def delete_staff(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)

    if user.access_level != 5:
        return HttpResponseForbidden("Access denied")

    user.delete()
    create_log(request.user, "Deleted User")
    return redirect('hr:kgn_staffs')


@admins
def reset_trials(request, user_id):

    user_to_reset = get_object_or_404(CustomUser, id=user_id)
    user_to_reset.trials = 4
    user_to_reset.is_restricted = False
    user_to_reset.save()

    messages.success(
        request, f"Trials reset successfully for {user_to_reset.username}. They can submit their staff No again.")

    return redirect('hr:system_users')


@admins
def delete_users_with_access_level_5(request):
    if request.method == 'POST':
        CustomUser.objects.filter(access_level=5).delete()
        create_log(request.user, "Deleted Staff")
        return redirect('hr:kgn_staffs')

    return render(request, 'hr/staffs.html')


@admins
def classes(request):
    classes = Class.objects.all()

    context = {
        'classes': classes,
    }

    return render(request, 'hr/classes.html', context)


@admins
def create_class(request):
    if request.method == 'POST':
        form = ClassForm(request.POST)
        if form.is_valid():
            form.save()
            create_log(request.user, "Added Class")
            messages.success(request, "Class Created succesfully")

            return redirect('hr:classes')
    else:
        form = ClassForm()
    return render(request, 'hr/create_class.html', {'form': form})


@admins
def edit_class(request, class_id):

    class_instance = get_object_or_404(Class, id=class_id)

    if request.method == 'POST':
        form = ClassForm(request.POST, instance=class_instance)
        if form.is_valid():
            form.save()
            create_log(request.user, "Updated Class")
            messages.success(request, "Class Updated succesfully")
            return redirect('hr:classes')
    else:
        form = ClassForm(instance=class_instance)

    return render(request, 'hr/create_class.html', {'form': form, 'class': class_instance})


@admins
def delete_class(request, class_id):
    class_instance = get_object_or_404(Class, id=class_id)
    class_instance.delete()
    create_log(request.user, "Edited Classs")
    return redirect('hr:classes')


@admins
def toggle_user_active_status(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    user.is_active = not user.is_active
    create_log(request.user, "Update user Status")
    user.save()

    return redirect(request.META.get('HTTP_REFERER', '/'))


@admins
def toggle_hired(request, vacancy_id):
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)

    user = request.user
    job_type = vacancy.job_type.name

    is_superuser = user.is_superuser
    is_ict = user.function == 10 or is_superuser
    is_hradmin = user.function == 1 or is_ict

    can_close = (
        (job_type in ['Careers', 'Internal'] and is_hradmin) or
        (job_type in ['Internship', 'Industrial Attachment']
         and is_hradmin)
    )

    shortlisted_applicants_exist = Application.objects.filter(
        vacancy=vacancy, shortlisted=True).exists()

    if vacancy.hired:

        vacancy.hired = False
        vacancy.save()
        create_log(request.user, "Updated vacancy Status")
        messages.success(
            request, f"Vacancy '{vacancy.title}' has been opened.")
    else:
        if shortlisted_applicants_exist:

            vacancy.hired = True

            if can_close:

                vacancy.save()
                send_emails_to_applicants(vacancy)
                messages.success(
                    request, f"Vacancy '{vacancy.title}' has been filled and notifications have been sent to the shortlisted applicants.")
            else:
                messages.error(
                    request, 'You do not have permission to Complete this Action')
        else:

            messages.error(
                request, f"Vacancy '{vacancy.title}' Failed to be closed and and the emails was not sent")

    return redirect(request.META.get('HTTP_REFERER', '/'))


@admins
def update_registrants(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'POST':
        form = RegistrantsEditForm(request.POST, instance=user)
        if form.is_valid():
            try:
                form.save()
                create_log(request.user, "Updated user Details")
                messages.success(
                    request, 'Registrants Details updated successfully.')
                return redirect('hr:system_users')
            except Exception as e:
                messages.error(
                    request, f"An error occurred while updating user details: {str(e)}")
        else:

            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
    else:
        form = RegistrantsEditForm(instance=user)

    return render(request, 'hr/edit_users.html', {'form': form, 'user': user})


@admins
def thanks_message(request):
    try:
        thanks_message = ThanksMessage.objects.get()
    except ThanksMessage.DoesNotExist:
        thanks_message = None

    if request.method == 'POST':
        form = ThanksMessageForm(request.POST, instance=thanks_message)
        if form.is_valid():
            form.save()
            messages.success(request, "Feedback Message Updated succesfully")
            return redirect(request.META.get('HTTP_REFERER', '/'))
    else:
        form = ThanksMessageForm(instance=thanks_message)

    return render(request, 'hr/message.html', {'form': form})


@admins
def logs(request):
    logs = Log.objects.all()

    username = request.GET.get('username')
    email = request.GET.get('email')
    if username:
        logs = logs.filter(user__username=username)

    if email:
        logs = logs.filter(user__email=email)

    logs = logs.order_by('-timestamp')[:100]

    return render(request, 'hr/logs.html', {'logs': logs})
