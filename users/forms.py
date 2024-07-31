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
            {'class': 'form-control', 'placeholder': 'Password', 'id': 'password'})
        self.fields['password2'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Confirm Password', 'id': 'password'})

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
        fields = ['username', 'first_name', 'last_name',
                  'email', 'id_number', 'staff_no']

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
        self.fields['id_number'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'ID Number'})
        self.fields['staff_no'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Staff Number'})

        # Make fields optional if needed, e.g.:
        # self.fields['id_number'].required = False
        # self.fields['staff_no'].required = False


class RegistrantsEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name',
                  'email', 'id_number']

    def __init__(self, *args, **kwargs):
        super(RegistrantsEditForm, self).__init__(*args, **kwargs)

        # Add CSS classes and placeholders to form fields
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

        # Make fields optional if needed, e.g.:
        # self.fields['id_number'].required = False
        # self.fields['staff_no'].required = False


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Username or Email'
            }
        ),
        label=""
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Password',
                'id': 'password'
            }
        ),
        label=""
    )


class SetPasswordForm(SetPasswordForm):
    old_password = forms.CharField(
        label=("Current Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
    )

    class Meta:
        model = get_user_model()
        fields = ['old_password', 'new_password1', 'new_password2']


class ResetPasswordForm(SetPasswordForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        # Remove the old_password field for password reset
        del self.fields['old_password']

    class Meta:
        model = get_user_model()
        fields = ['new_password1', 'new_password2']


class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(
            attrs={'class': 'form-control', 'placeholder': 'Email'}
        )
    )

    id_number = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={'class': 'form-control',
                   'placeholder': 'Staff No without Kgn'}
        ),
        label='Staff Number',
        required=True
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
