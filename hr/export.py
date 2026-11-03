import re
from html import unescape

import openpyxl
from openpyxl.styles import Alignment, Font
from django.http import HttpResponse
from django.utils.html import strip_tags

from users.models import Resume, WorkExperience
from .educational_level import *
from .logs import *


# -------------------------------------------------
# Excel safety helper (CRITICAL)
# -------------------------------------------------
ILLEGAL_CHARACTERS_RE = re.compile(r'[\x00-\x08\x0B\x0C\x0E-\x1F]')


def clean_excel_value(value):
    """
    Clean values before writing to Excel.
    Removes illegal/control characters.
    """
    if value is None:
        return ''

    if isinstance(value, str):
        value = unescape(value)          # Decode HTML entities
        value = strip_tags(value)        # Remove HTML tags
        value = ILLEGAL_CHARACTERS_RE.sub('', value)
        return value.strip()

    return value


def export_applications_to_excel(request, applications):
    """
    Export application data to an Excel file (Excel-safe).
    """
    create_log(request.user, "Exported Applications")

    data = []

    # -------------------------------------------------
    # Handle empty queryset safely
    # -------------------------------------------------
    first_application = applications.first()
    if not first_application:
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="applications.xlsx"'

        wb = openpyxl.Workbook()
        wb.save(response)

        return response

    # -------------------------------------------------
    # Process applications
    # -------------------------------------------------
    for application in applications:
        user = application.applicant

        try:
            resume = user.resume
        except Resume.DoesNotExist:
            resume = Resume.objects.create(
                user=user,
                full_name=f"{user.first_name} {user.last_name}",
                email_address=user.email,
            )

        basic_education = user.basic_education.all()[:2]
        further_studies = user.further_studies.all()[:3]
        work_experience = user.work_experiences.all()[:3]
        certifications = user.certifications.all()[:3]
        memberships = user.memberships.all()[:3]
        referees = user.referees.all()[:3]

        contacts = f"{resume.phone or ''}\n{resume.email_address or ''}"

        educational_level = (
            resume.educational_level
            or get_user_highest_educational_level(user.id)
        )

        educational_level_name = (
            educational_level.name if educational_level else ''
        )

        application_data = {
            'Username/Staff No.': user.username,
            'Full Name': resume.full_name,
            'Contact Details': contacts,
            'Gender': resume.gender or '',
            'Disability': 'Yes' if resume.disability else 'No',
            'Ethnicity': (
                resume.ethnicity.name if resume.ethnicity else ''
            ),
            'Highest Educational Level': educational_level_name,
            'High School': '',
            'College/University': '',
            'Professional Certifications': '',
            'Professional Membership': '',
            'Work Experience': '',
            'Referees': '',
            'Date Applied': (
                application.application_date.strftime("%Y-%m-%d %H:%M:%S")
                if application.application_date else ''
            ),
            'Reference Number': application.reference_number,
            'Status': (
                'Qualified'
                if application.qualify else 'Not Qualified'
            ),
            'Shortlisted': (
                'Yes'
                if application.shortlisted else 'No'
            ),
        }

        # -------------------------------------------------
        # BASIC EDUCATION
        # -------------------------------------------------
        if basic_education:
            block = []

            for edu in basic_education:
                block.append(
                    f"School: {clean_excel_value(edu.name_of_the_school)}\n"
                    f"Start Year: {clean_excel_value(edu.date_started)}\n"
                    f"End Year: {clean_excel_value(edu.date_ended)}\n"
                    f"Grade Attained: {clean_excel_value(edu.grade_attained)}"
                )

            application_data['High School'] = "\n\n".join(block)

        # -------------------------------------------------
        # FURTHER STUDIES
        # -------------------------------------------------
        if further_studies:
            block = []

            for study in further_studies:
                block.append(
                    f"Institution: {clean_excel_value(study.institution_name)}\n"
                    f"Certification: "
                    f"{clean_excel_value(study.certifications.name if study.certifications else '')}\n"
                    f"Course: {clean_excel_value(study.course_undertaken)}\n"
                    f"Start Date: "
                    f"{study.date_started.strftime('%Y-%m-%d') if study.date_started else ''}\n"
                    f"End Date: "
                    f"{study.date_ended.strftime('%Y-%m-%d') if study.date_ended else ''}\n"
                    f"Grade: {clean_excel_value(study.grade)}"
                )

            application_data['College/University'] = "\n\n".join(block)

        # -------------------------------------------------
        # CERTIFICATIONS
        # -------------------------------------------------
        if certifications:
            block = []

            for cert in certifications:
                block.append(
                    f"Name: {clean_excel_value(cert.name)}\n"
                    f"Body: "
                    f"{clean_excel_value(cert.certifying_body.name if cert.certifying_body else '')}\n"
                    f"Date Attained: "
                    f"{cert.date_attained.strftime('%Y-%m-%d') if cert.date_attained else ''}"
                )

            application_data['Professional Certifications'] = "\n\n".join(block)

        # -------------------------------------------------
        # MEMBERSHIPS
        # -------------------------------------------------
        if memberships:
            block = []

            for m in memberships:
                block.append(
                    f"Title: {clean_excel_value(m.membership_title)}\n"
                    f"Number: {clean_excel_value(m.membership_number)}\n"
                    f"Body: {clean_excel_value(m.membership_body)}\n"
                    f"Date Joined: "
                    f"{m.date_joined.strftime('%Y-%m-%d') if m.date_joined else ''}"
                )

            application_data['Professional Membership'] = "\n\n".join(block)

        # -------------------------------------------------
        # WORK EXPERIENCE
        # -------------------------------------------------
        if work_experience:
            block = []
            total_months = 0

            for exp in work_experience:
                start = (
                    exp.date_started.strftime('%Y-%m-%d')
                    if exp.date_started else ''
                )

                end = (
                    exp.date_ended.strftime('%Y-%m-%d')
                    if exp.date_ended else 'In Progress'
                )

                responsibilities = clean_excel_value(
                    exp.responsibilities or ''
                )

                block.append(
                    f"Company: {clean_excel_value(exp.company_name)}\n"
                    f"Position: {clean_excel_value(exp.position)}\n"
                    f"Start Date: {start}\n"
                    f"End Date: {end}\n"
                    f"Address: {clean_excel_value(exp.company_address)}\n"
                    f"Phone: {clean_excel_value(exp.company_phone)}\n"
                    f"Responsibilities: {responsibilities}"
                )

                if exp.date_started and exp.date_ended:
                    delta = exp.date_ended - exp.date_started
                    total_months += delta.days // 30

            years, months = divmod(total_months, 12)

            block.append(
                f"Total Experience: {years} years {months} months"
            )

            application_data['Work Experience'] = "\n\n".join(block)

        # -------------------------------------------------
        # REFEREES
        # -------------------------------------------------
        if referees:
            block = []

            for r in referees:
                block.append(
                    f"Name: {clean_excel_value(r.full_name)}\n"
                    f"Organization: {clean_excel_value(r.organization)}\n"
                    f"Designation: {clean_excel_value(r.designation)}\n"
                    f"Phone: {clean_excel_value(r.phone)}\n"
                    f"Email: {clean_excel_value(r.email)}"
                )

            application_data['Referees'] = "\n\n".join(block)

        data.append(application_data)

    # -------------------------------------------------
    # Excel headers
    # -------------------------------------------------
    headers = [
        'Username/Staff No.',
        'Full Name',
        'Contact Details',
        'Gender',
        'Disability',
        'Ethnicity',
        'Highest Educational Level',
        'High School',
        'College/University',
        'Professional Certifications',
        'Professional Membership',
        'Work Experience',
        'Referees',
        'Date Applied',
        'Reference Number',
        'Status',
        'Shortlisted'
    ]

    # -------------------------------------------------
    # Create workbook
    # -------------------------------------------------
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Applications"

    title = clean_excel_value(
        f"{first_application.vacancy.title} / "
        f"{first_application.vacancy.ref} Applications"
    )

    # -------------------------------------------------
    # Title row
    # -------------------------------------------------
    title_cell = ws.cell(row=1, column=1, value=title)

    title_cell.font = Font(size=14, bold=True)
    title_cell.alignment = Alignment(horizontal='center')

    ws.merge_cells(
        start_row=1,
        start_column=1,
        end_row=1,
        end_column=len(headers)
    )

    # -------------------------------------------------
    # Header row
    # -------------------------------------------------
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=2, column=col, value=header)

        cell.font = Font(bold=True)
        cell.alignment = Alignment(
            wrap_text=True,
            horizontal='center',
            vertical='center'
        )

        ws.column_dimensions[
            openpyxl.utils.get_column_letter(col)
        ].width = 28

    # -------------------------------------------------
    # Data rows
    # -------------------------------------------------
    for row, record in enumerate(data, 3):

        for col, header in enumerate(headers, 1):

            value = clean_excel_value(record.get(header, ''))

            cell = ws.cell(
                row=row,
                column=col,
                value=value
            )

            cell.alignment = Alignment(
                wrap_text=True,
                vertical='top'
            )

        ws.row_dimensions[row].height = 120

    # -------------------------------------------------
    # Response
    # -------------------------------------------------
    response = HttpResponse(
        content_type=(
            'application/vnd.openxmlformats-officedocument.'
            'spreadsheetml.sheet'
        )
    )

    filename = (
        f'applications_for_'
        f'{clean_excel_value(first_application.vacancy.title)}_'
        f'{clean_excel_value(first_application.vacancy.ref)}.xlsx'
    )

    response['Content-Disposition'] = (
        f'attachment; filename="{filename}"'
    )

    wb.save(response)

    return response