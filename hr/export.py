import openpyxl
from openpyxl.styles import Alignment
from django.http import HttpResponse
import re
from users.models import Resume
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
        
        educational_level_name = resume.educational_level.name if resume.educational_level else ''

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

        if basic_education:
            application_data['High School'] = "\n\n".join([
                f"School: {edu.name_of_the_school}\nStart Year: {edu.date_started}\nEnd Year: {edu.date_ended}\nGrade: {edu.grade_attained}"
                for edu in basic_education
            ])

        if further_studies:
            application_data['College/University'] = "\n\n".join([
                f"Institution: {study.institution_name}\nCertification: {study.certifications.name if study.certifications else ''}\n"
                f"Course: {study.course_undertaken}\nStart: {study.date_started.strftime('%Y-%m-%d') if study.date_started else ''}\n"
                f"End: {study.date_ended.strftime('%Y-%m-%d') if study.date_ended else ''}\nGrade: {study.grade}"
                for study in further_studies
            ])

        if certifications:
            application_data['Professional Certifications'] = "\n\n".join([
                f"Name: {cert.name}\nBody: {cert.certifying_body.name if cert.certifying_body else ''}\nDate: {cert.date_attained.strftime('%Y-%m-%d') if cert.date_attained else ''}"
                for cert in certifications
            ])

        if memberships:
            application_data['Professional Membership'] = "\n\n".join([
                f"Title: {membership.membership_title}\nNumber: {membership.membership_number}\nBody: {membership.membership_body}\nJoined: {membership.date_joined.strftime('%Y-%m-%d') if membership.date_joined else ''}"
                for membership in memberships
            ])

        if work_experience:
            application_data['Work Experience'] = "\n\n".join([
                f"Company: {experience.company_name}\nPosition: {experience.position}\n"
                f"Start: {experience.date_started.strftime('%Y-%m-%d') if experience.date_started else ''}\n"
                f"End: {experience.date_ended.strftime('%Y-%m-%d') if experience.date_ended else 'Present' if experience.currently_working else ''}\n"
                f"Address: {experience.company_address}\nPhone: {experience.company_phone}\nResponsibilities: {experience.responsibilities}"
                for experience in work_experience
            ])

        if referees:
            application_data['Referees'] = "\n\n".join([
                f"Name: {referee.full_name}\nOrganization: {referee.organization}\nDesignation: {referee.designation}\nPhone: {referee.phone}\nEmail: {referee.email}"
                for referee in referees
            ])

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
        ws.column_dimensions[openpyxl.utils.get_column_letter(col_num)].width = 25

    for row_num, application_data in enumerate(data, 3):
        for col_num, header in enumerate(headers, 1):
            value = application_data.get(header, '')
            cell = ws.cell(row=row_num, column=col_num, value=value)
            cell.alignment = Alignment(wrap_text=True)

    # **Sanitize the Filename**
    vacancy_title = re.sub(r'[^\w\-_]', '_', application.vacancy.title)
    vacancy_ref = re.sub(r'[^\w\-_]', '_', application.vacancy.ref)
    safe_filename = f"applications_for_{vacancy_title}_{vacancy_ref}.xlsx"

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{safe_filename}"; filename*=UTF-8\'\'{safe_filename}'
    wb.save(response)

    return response
