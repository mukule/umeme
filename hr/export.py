import openpyxl
from openpyxl.styles import Alignment
from django.http import HttpResponse
from users.models import Resume, WorkExperience
from .educational_level import *
from .logs import *


def export_applications_to_excel(request, applications):
    """
    Export application data to an Excel file.
    """
    create_log(request.user, "Exported Applications")
    data = []
    for application in applications:
        user = application.applicant
        try:
            resume = user.resume
        except Resume.DoesNotExist:
            # Create a new Resume if it doesn't exist
            full_name = f"{user.first_name} {user.last_name}"
            resume = Resume.objects.create(
                user=user,
                full_name=full_name,
                email_address=user.email,
            )

        basic_education = user.basic_education.all()[:2]
        further_studies = user.further_studies.all()[:3]
        work_experience = user.work_experiences.all()[:3]
        certifications = user.certifications.all()[:3]
        memberships = user.memberships.all()[:3]
        referees = user.referees.all()[:3]

        full_name = resume.full_name
        username = user.username
        contacts = f"{resume.phone}\n{resume.email_address}"

        educational_level = resume.educational_level or get_user_highest_educational_level(
            user.id)
        educational_level_name = educational_level.name if educational_level else ''

        application_data = {
            'Username/Staff No.': username,
            'Full Name': full_name,
            'Contact Details': contacts,
            'Gender': resume.gender if resume.gender else '',
            'Disability': 'Yes' if resume.disability else 'No',
            'Ethnicity': resume.ethnicity.name if resume.ethnicity else '',
            'Highest Educational Level': educational_level_name,
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

        # Handle Basic Education
        if basic_education:
            academic_data = ''
            for edu in basic_education:
                institution_name = f"School: {edu.name_of_the_school}"
                start_year = f"Start Year: {edu.date_started}"
                end_year = f"End Year: {edu.date_ended}"
                grade = f"Grade attained: {edu.grade_attained}"
                academic_data += f"{institution_name}\n{start_year}\n{end_year}\n{grade}\n\n"
            application_data['High School'] = academic_data

        # Handle Further Studies
        if further_studies:
            further_studies_data = ''
            for study in further_studies:
                institution_name = f"Institution Name: {study.institution_name}"
                certification_name = f"Certification: {study.certifications.name if study.certifications else ''}"
                course_undertaken = f"Course Undertaken: {study.course_undertaken}"
                start_date = f"Start Date: {study.date_started.strftime('%Y-%m-%d') if study.date_started else ''}"
                end_date = f"End Date: {study.date_ended.strftime('%Y-%m-%d') if study.date_ended else ''}"
                grade = f"Grade: {study.grade}"
                further_studies_data += f"{institution_name}\n{certification_name}\n{course_undertaken}\n{start_date}\n{end_date}\n{grade}\n\n"
            application_data['College/University'] = further_studies_data

        # Handle Certifications
        if certifications:
            certifications_data = ''
            for cert in certifications:
                name = f"Name: {cert.name}"
                certifying_body_name = f"Certifying Body: {cert.certifying_body.name if cert.certifying_body else ''}"
                date_attained = f"Date Attained: {cert.date_attained.strftime('%Y-%m-%d') if cert.date_attained else ''}"
                certifications_data += f"{name}\n{certifying_body_name}\n{date_attained}\n\n"
            application_data['Professional Certifications'] = certifications_data

        # Handle Memberships
        if memberships:
            memberships_data = ''
            for membership in memberships:
                title = f"Membership Title: {membership.membership_title}"
                number = f"Membership Number: {membership.membership_number}"
                body = f"Membership Body: {membership.membership_body}"
                joined_date = f"Date Joined: {membership.date_joined.strftime('%Y-%m-%d') if membership.date_joined else ''}"
                memberships_data += f"{title}\n{number}\n{body}\n{joined_date}\n\n"
            application_data['Professional Membership'] = memberships_data

        # Handle Work Experience
        if work_experience:
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

                if experience.date_started and experience.date_ended:
                    delta = experience.date_ended - experience.date_started
                    years_worked = delta.days // 365
                    months_worked = (delta.days % 365) // 30
                    work_experience_data += f"Years Worked: {years_worked} years\nMonths Worked: {months_worked} months\n\n"
                    total_years += years_worked
                    total_months += months_worked

                work_experience_data += "\n"

            additional_years, remaining_months = divmod(total_months, 12)
            total_years += additional_years
            total_experience = f"Total Experience: {total_years} years and {remaining_months} months"
            work_experience_data += total_experience

            application_data['Work Experience'] = work_experience_data

        # Handle Referees
        if referees:
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

    wb = openpyxl.Workbook()
    ws = wb.active

    title = f"{application.vacancy.title} / {application.vacancy.ref} Applications"
    title_row = ws.cell(row=1, column=1, value=title)
    title_row.alignment = Alignment(horizontal='center')
    title_row.font = openpyxl.styles.Font(size=14, bold=True)

    for col_num, header in enumerate(headers, 1):
        ws.cell(row=2, column=col_num, value=header)
        ws.column_dimensions[openpyxl.utils.get_column_letter(
            col_num)].width = 25

    for row_num, application_data in enumerate(data, 3):
        for col_num, header in enumerate(headers, 1):
            value = application_data.get(header, '')
            cell = ws.cell(row=row_num, column=col_num, value=value)
            cell.alignment = Alignment(wrap_text=True)

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="applications_for_{application.vacancy.title}_{application.vacancy.ref}.xlsx"'
    wb.save(response)

    return response
