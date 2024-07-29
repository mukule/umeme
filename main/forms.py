from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from users.models import CustomUser
from users.models import *
from django.core.exceptions import ValidationError
import pycountry
from tinymce.widgets import TinyMCE

MARITAL_STATUS_CHOICES = MaritalStatus.objects.all().values_list('name', 'name')
GENDER_CHOICES = Gender.objects.all().values_list('name', 'name')
COUNTY_CHOICES = County.objects.all().values_list('name', 'name')
GRADE_CHOICES = [
    ('', 'Select Grade Attained'),
    ('A', 'A'),
    ('B+', 'B+'),
    ('B', 'B'),
    ('B-', 'B-'),
    ('C+', 'C+'),
    ('C', 'C'),
    ('C-', 'C-'),
    ('D+', 'D+'),
    ('D', 'D'),
    ('D-', 'D-'),
    ('E', 'E'),
]


# Generate country choices using pycountry
COUNTRY_CHOICES = [(country.alpha_2, country.name)
                   for country in pycountry.countries]


class ResumeForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
        label='Full Name',

    )
    email_address = forms.EmailField(
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
        label='Email Address',

    )
    phone = forms.CharField(
        max_length=10,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Phone'}),
        label='Phone',

    )
    id_number = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={'class': 'form-control', 'placeholder': 'ID Number'}),
        label='ID Number',
        required=True
    )

    dob = forms.DateField(
        widget=forms.DateInput(
            attrs={'class': 'form-control', 'placeholder': 'Date of Birth', 'type': 'date'}),
        label='Date of Birth',

    )
    country_of_birth = forms.ChoiceField(
        choices=[('', 'Select Country')] + COUNTRY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Country of Birth',

    )
    country_of_residence = forms.ChoiceField(
        choices=[('', 'Select Country')] + COUNTRY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Country of Residence',

    )
    county_of_birth = forms.ChoiceField(
        choices=[('', 'Select County of Birth')] + list(COUNTY_CHOICES),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='County of Birth', required=False


    )
    county_of_residence = forms.ChoiceField(
        choices=[('', 'Select County of Residence')] + list(COUNTY_CHOICES),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='County of Residence', required=False


    )
    ethnicity = forms.ModelChoiceField(
        queryset=Ethnicity.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Ethnicity',
        empty_label='Select Ethnicity'

    )
    gender = forms.ChoiceField(
        choices=[('', 'Select Gender')] + list(GENDER_CHOICES),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Gender',

    )
    disability = forms.ChoiceField(
        choices=[('', 'Select Disability Status')] +
        [(True, 'Yes'), (False, 'No')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Are you a person with Disability ?',
        required=False
    )

    disability_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Disability Number'}),
        label='Disability Number',

    )
    marital_status = forms.ChoiceField(
        choices=[('', 'Select Marital Status')] + list(MARITAL_STATUS_CHOICES),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Marital Status',

    )
    educational_level = forms.ModelChoiceField(
        queryset=EducationalLevel.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Highest Education Level',
        empty_label='Select Highest Education Level'

    )
    field_of_study = forms.ModelChoiceField(
        queryset=FieldOfStudy.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Field of Study',
        empty_label='Select Field of Study'

    )

    class Meta:
        model = Resume
        fields = [
            'full_name', 'email_address', 'phone', 'id_number', 'dob',
            'country_of_birth', 'country_of_residence', 'county_of_birth', 'county_of_residence', 'ethnicity',
            'gender', 'disability', 'disability_number', 'marital_status',
            'educational_level', 'field_of_study'
        ]


class EducationalInformationForm(forms.ModelForm):
    name_of_the_school = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Name of the School'}),
        label='Name of the School', required=True
    )
    certification = forms.ChoiceField(
        choices=BasicEducation.certification_choices,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Certification', required=True
    )
    date_started = forms.DateField(
        widget=forms.DateInput(
            attrs={'class': 'form-control', 'placeholder': 'Date Started', 'type': 'date'}),
        label='Date Started', required=True
    )
    date_ended = forms.DateField(
        widget=forms.DateInput(
            attrs={'class': 'form-control', 'placeholder': 'Date Ended', 'type': 'date'}),
        label='Date Ended', required=True
    )
    grade_attained = forms.ChoiceField(
        choices=GRADE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Grade Attained', required=True
    )
    certificate = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        label='Certificate File(pdf only, Not more than 1Mb)', required=True
    )

    def clean_certificate(self):
        certificate = self.cleaned_data.get('certificate')
        if certificate:
            if not certificate.name.endswith('.pdf'):
                raise forms.ValidationError('Only PDF files are allowed.')
            if certificate.size > 1 * 1024 * 1024:  # 5MB
                raise forms.ValidationError(
                    'File size must be no more than 1MB.')
        return certificate

    class Meta:
        model = BasicEducation
        fields = [
            'name_of_the_school', 'certification',
            'date_started', 'date_ended', 'grade_attained', 'certificate'
        ]


class FurtherStudiesForm(forms.ModelForm):
    certification_choices = FurtherStudiesCertification.objects.all()

    institution_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Institution Name'}),
        label='Institution Name', required=True
    )
    certifications = forms.ModelChoiceField(
        queryset=EducationalLevel.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Levels of study', empty_label="--Select Levels of Study--", required=True
    )
    course_undertaken = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Course Undertaken'}),
        label='Course Undertaken', required=True
    )
    date_started = forms.DateField(
        widget=forms.DateInput(
            attrs={'class': 'form-control', 'placeholder': 'Date Started', 'type': 'date'}),
        label='Date Started', required=True
    )
    date_ended = forms.DateField(
        widget=forms.DateInput(
            attrs={'class': 'form-control', 'placeholder': 'Date Ended', 'type': 'date'}),
        label='Date Ended', required=True
    )
    grade = forms.ModelChoiceField(
        queryset=Class.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Class Attained',
        required=True,
        empty_label="--Select Class--",
    )
    certificate = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        label='Certificate File(pdfs only Not more than 1mb)', required=True
    )

    def clean_certificate(self):
        certificate = self.cleaned_data.get('certificate')
        if certificate:
            if not certificate.name.endswith('.pdf'):
                raise forms.ValidationError('Only PDF files are allowed.')
            if certificate.size > 1 * 1024 * 1024:  # 5MB
                raise forms.ValidationError(
                    'File size must be no more than 1MB.')
        return certificate

    class Meta:
        model = FurtherStudies
        fields = [
            'institution_name', 'certifications', 'course_undertaken',
            'date_started', 'date_ended', 'grade', 'certificate'
        ]


class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ['name', 'certifying_body', 'date_attained', 'certificate']

    name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Certification Name'}),
        label='Certification Name', required=True
    )
    certifying_body = forms.ModelChoiceField(
        queryset=CertifyingBody.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Certifying Body', required=True,
        empty_label='Select Certifying Body'

    )
    date_attained = forms.DateField(
        widget=forms.DateInput(
            attrs={'class': 'form-control', 'placeholder': 'Date Attained', 'type': 'date'}),
        label='Date Awarded the Certificate', required=True
    )
    certificate = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        label='Certificate File(pdfs only, Not more than 1Mb)', required=True

    )

    def clean_certificate(self):
        certificate = self.cleaned_data.get('certificate')
        if certificate:
            if not certificate.name.endswith('.pdf'):
                raise ValidationError('Only PDF files are allowed.')
            if certificate.size > 1 * 1024 * 1024:  # 5MB
                raise ValidationError('File size must be no more than 5MB.')
        return certificate


class MembershipForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = ['membership_title', 'membership_number', 'membership_body',
                  'date_joined', 'certificate']

    membership_title = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Membership Title'}),
        label='Membership Title', required=True
    )
    membership_number = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Membership Number'}),
        label='Membership Number', required=True
    )
    date_joined = forms.DateField(
        widget=forms.DateInput(
            attrs={'class': 'form-control', 'placeholder': 'Date Joined', 'type': 'date'}),
        label='Date Awarded the certificate', required=True
    )
    certificate = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        label='Membership Certificate File (PDFs only, not more than 1MB)',
        required=True
    )
    membership_body = forms.ModelChoiceField(
        queryset=CertifyingBody.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Membership Body', required=True,
        empty_label='Select Membership Body'
    )

    def clean_certificate(self):
        certificate = self.cleaned_data.get('certificate')
        if certificate:
            if not certificate.name.endswith('.pdf'):
                raise forms.ValidationError('Only PDF files are allowed.')
            if certificate.size > 1 * 1024 * 1024:  # 1MB
                raise forms.ValidationError(
                    'File size must be no more than 1MB.')
        return certificate


class WorkExperienceForm(forms.ModelForm):
    class Meta:
        model = WorkExperience
        fields = ['company_name', 'position', 'date_started', 'date_ended',
                  'company_address', 'company_phone', 'responsibilities', 'currently_working']

    company_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Company Name'}),
        label='Company Name', required=True
    )
    position = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Position'}),
        label='Position', required=True
    )
    date_started = forms.DateField(
        widget=forms.DateInput(
            attrs={'class': 'form-control', 'placeholder': 'Date Started', 'type': 'date'}),
        label='Date Started', required=True
    )
    date_ended = forms.DateField(
        widget=forms.DateInput(
            attrs={'class': 'form-control', 'placeholder': 'Date Ended', 'type': 'date'}),
        label='Date Ended', required=False
    )
    company_address = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Company Address'}),
        label='Company Address', required=True
    )
    company_phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Company Phone'}),
        label='Company Phone', required=True
    )
    responsibilities = forms.CharField(
        widget=forms.Textarea(
            attrs={'class': 'form-control', 'placeholder': 'Responsibilities'}),
        label='Responsibilities', required=True
    )
    currently_working = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Current Position(Current Job)', required=False
    )


class RefereeForm(forms.ModelForm):
    class Meta:
        model = Referee
        fields = ['full_name', 'organization', 'designation', 'phone', 'email']

    full_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
        label='Full Name', required=True
    )
    organization = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Organization'}),
        label='Organization', required=True
    )
    designation = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Designation'}),
        label='Designation', required=True
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Phone'}),
        label='Phone', required=True
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': 'Email'}),
        label='Email', required=True
    )


class ProfessionalSummaryForm(forms.ModelForm):
    class Meta:
        model = ProfessionalSummary
        fields = ['career_objective']

    career_objective = forms.CharField(
        widget=TinyMCE(
            attrs={'id': 'mce1', 'class': 'form-control', 'placeholder': 'Executive Summery', 'rows': 5}),
        label=''
    )


class UpdateEducationalLevelForm(forms.ModelForm):
    educational_level = forms.ModelChoiceField(
        queryset=EducationalLevel.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Select the highest educational level"
    )

    class Meta:
        model = Resume
        fields = ['educational_level']
