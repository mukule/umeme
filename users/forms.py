from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.forms import PasswordResetForm
from .models import *


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        help_text='A valid email address, please.', required=True)

    id_number = forms.CharField(
        max_length=8, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ID Number'}))

    class Meta:
        model = get_user_model()
        fields = ['username', 'first_name', 'last_name',
                  'email', 'id_number', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)

        # Add CSS classes to form fields
        self.fields['username'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Username'})
        self.fields['first_name'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'First Name'})
        self.fields['last_name'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Last Name'})
        self.fields['email'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Email Address'})
        self.fields['id_number'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'ID Number'})
        self.fields['password1'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Confirm Password', 'id': 'show_hide_password'})

    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.id_number = self.cleaned_data['id_number']
        if commit:
            user.save()
        return user


class UserEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)

        # Add CSS classes and placeholders to form fields
        self.fields['username'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Username'})
        self.fields['first_name'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'First Name'})
        self.fields['last_name'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Last Name'})
        self.fields['email'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Email Address'})


class PortalManagementForm(UserCreationForm):
    email = forms.EmailField(
        help_text='A valid email address, please.', required=True)
    access_level = forms.ChoiceField(
        choices=CustomUser.ACCESS_LEVEL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
    )

    class Meta:
        model = get_user_model()
        fields = ['username', 'email',
                  'access_level', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(PortalManagementForm, self).__init__(
            *args, **kwargs)  # Use correct form class name

        # Add CSS classes to form fields
        self.fields['username'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Username'})
        self.fields['email'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Email Address'})
        self.fields['access_level'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Access Level'})
        self.fields['password1'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Confirm Password'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Username or Email'}),
        label="Username or Email*")

    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Password'}))

class SetPasswordForm(SetPasswordForm):
    old_password = forms.CharField(
        label=("Current Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
    )

    class Meta:
        model = get_user_model()
        fields = ['old_password', 'new_password1', 'new_password2']


class CustomPasswordResetForm(PasswordResetForm):
    id_number = forms.CharField(
        max_length=8,
        required=True,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'ID Number'})
    )

    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': 'Email'})
    )


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'profile', 'email']


class ExcelImportForm(forms.Form):
    excel_file = forms.FileField()


class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['staff_no', 'name']


class CustomUserCreationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email']


class UpdateFunctionForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        # Include 'username' and 'email' fields
        fields = ['function', 'username', 'email']

    def __init__(self, *args, **kwargs):
        super(UpdateFunctionForm, self).__init__(*args, **kwargs)
        # Set the 'readonly' attribute for 'username' and 'email' fields
        self.fields['username'].widget.attrs['readonly'] = True
        self.fields['email'].widget.attrs['readonly'] = True
        self.fields['function'].widget = forms.Select(
            choices=CustomUser.FUNCTION_CHOICES)
