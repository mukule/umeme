from django import forms
from vacancies.models import *
from django.contrib.auth.forms import UserCreationForm
from users.models import CustomUser
from tinymce.widgets import TinyMCE
from django import forms
from vacancies.models import *


class VacancyForm(forms.ModelForm):

    vacancy_type = forms.ModelChoiceField(
        queryset=JobType.objects.all(),
        empty_label='--Select Job Type--',
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
        label=''
    )

    min_educational_level = forms.ModelChoiceField(
        queryset=EducationalLevel.objects.all(),
        empty_label='--Select Minimum Education Level--',
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
        label='Educational Level'
    )

    job_discipline = forms.ModelChoiceField(
        queryset=JobDiscipline.objects.all(),
        empty_label='--Select Job Discipline--',
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
        label=''
    )

    position_responsibilities = forms.CharField(
        widget=TinyMCE(attrs={'id': 'mce1', 'class': 'form-control'}),
        label=''
    )

    description = forms.CharField(
        widget=TinyMCE(attrs={'id': 'mce2', 'class': 'form-control'}),
        label=''
    )

    class Meta:
        model = Vacancy
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vacancy Title'}),
            'ref': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vacancy Reference'}),
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
            'title': '',
            'ref': '',
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
    text = forms.CharField(widget=TinyMCE(
        attrs={'id': 'mce3', 'class': 'form-control'})),


class JobTypeForm(forms.ModelForm):
    class Meta:
        model = JobType
        fields = ['name', 'description', 'banner', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'banner': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'icon': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }
