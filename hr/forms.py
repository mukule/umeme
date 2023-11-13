from django import forms
from vacancies.models import *
from django.contrib.auth.forms import UserCreationForm
from users.models import CustomUser
from ckeditor.widgets import CKEditorWidget

from django import forms


class VacancyForm(forms.ModelForm):
    class Meta:
        model = Vacancy
        fields = '__all__'
        widgets = {
            'vacancy_type': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vacancy Title'}),
            'ref': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vacancy Reference'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Opportunity Description'}),
            'position_responsibilities': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Position Responsibilities'}),
            'reports_to': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Reports To'}),
            'date_open': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Date Open', 'type': 'date'}),
            'date_close': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Date Close', 'type': 'date'}),
            'posts_needed': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Posts Needed'}),
            'min_work_experience': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Minimum Work Experience'}),
            'min_educational_level': forms.Select(attrs={'class': 'form-control'}),
            'published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'job_discipline': forms.Select(attrs={'class': 'form-control'}),
            'certifications_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'college_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'membership_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'vacancy_type': '',
            'title': '',
            'ref': '',
            'description': '',
            'position_responsibilities': 'Position Responsibilities',
            'reports_to': 'Reports to',
            'date_open': 'Date Open',
            'date_close': 'Date Close',
            'posts_needed': 'Posts Needed',
            'min_work_experience': 'Minimum Work Experience',
            'min_educational_level': 'Educational Level',
            'published': 'Published',
            'job_discipline': '',
            'certifications_required': 'Certifications Required',
            'college_required': 'College/University/Further studies',
            'membership_required': 'Professional Membership',
        }


class JobDisciplineForm(forms.ModelForm):
    class Meta:
        model = JobDiscipline
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job Discipline Name'}),
        }
        labels = {
            'name': '',
        }


class CertifyingBodyForm(forms.ModelForm):
    class Meta:
        model = CertifyingBody
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Certifying Body Name'}),
        }


class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ['name', 'certifying_body']

    def __init__(self, *args, **kwargs):
        super(CertificateForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Certificate Name'})
        self.fields['certifying_body'].widget.attrs.update(
            {'class': 'form-control'})


class FieldOfStudyForm(forms.ModelForm):
    class Meta:
        model = FieldOfStudy
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super(FieldOfStudyForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control'})


class EthnicityForm(forms.ModelForm):
    class Meta:
        model = Ethnicity
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class AdminForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': 'Email Address'})
    )

    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Username'})
    )

    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Password'}),
    )

    password2 = forms.CharField(
        label="Confirm Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}),
    )

    class Meta:
        model = CustomUser
        fields = ['access_level', 'email',
                  'username', 'password1', 'password2']


class TermsForm(forms.Form):
    text = forms.CharField(widget=CKEditorWidget(attrs={'id': 'terms_text'}))
