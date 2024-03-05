from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import logging
from .models import Staff
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, login
from .forms import *
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .decorators import user_not_authenticated
from django.contrib.auth import authenticate, login
from .decorators import *
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from .tokens import account_activation_token
from .forms import SetPasswordForm
from .forms import PasswordResetForm
from django.db.models.query_utils import Q
from django.contrib.auth.decorators import user_passes_test
import random
import string
from urllib.parse import urlencode
from django.http import QueryDict
from vacancies.models import *
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import check_password

def is_system_admin(user):
    return user.is_superuser or (user.access_level == 'system admin')


def not_authorized(request):
    return render(
        request,
        template_name="admin/not_authorized.html"
    )



@user_not_authenticated
def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            activateEmail(request, user, form.cleaned_data.get('email'))
            
            success_message = f'Dear {user}, please go to your email {form.cleaned_data.get("email")} inbox and click on the received activation link to confirm and complete the registration. Note: Check your spam folder.'
            
            messages.success(request, success_message)
            return redirect('users:register')

        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    else:
        form = UserRegistrationForm()

    return render(
        request=request,
        template_name="users/register.html",
        context={"form": form}
    )


def activateEmail(request, user, to_email):
    mail_subject = 'KenGen Careers Portal - Activate your user account.'
    message = render_to_string('users/template_activate_account.html', {
        'user': user,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, from_email='hrm@careers.kengen.co.ke', to=[to_email], cc=['nelson.masibo@kenyaweb.com'],)
    email.extra_headers['Sender'] = 'nelson@kenyaweb.co.ke'
    
    if email.send():
        return True
    else:
        return False


def activate(request, uidb64, token):
    User = get_user_model()
    success_message = error_message = None

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        success_message = 'Thank you for your email confirmation. Now you can log in to your account.'
        messages.success(request, success_message)
        return redirect('users:login')
    
        
    else:
        error_message = 'Activation link is invalid, or has expired, Please Conduct admin for more Details'

    return render(
        request=request,
        template_name="main/index.html",
        context={"error_message": error_message}
    )

def secure(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        # Log in the user
        login(request, user)

        messages.success(request, 'Password Updated succesfully.')
        return redirect('users:password_change')
    else:
        messages.error(request, 'Password change link is invalid!')

    return redirect('/')


def generate_random_password(length=10):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for _ in range(length))
    return password


@user_passes_test(is_system_admin, login_url='users:not_authorized')
def hrs(request):
    if request.method == "POST":
        form = PortalManagementForm(request.POST)
        if form.is_valid():
            user = form.save(commit=True)
            access_level_display = user.get_access_level_display()
            success_message = f'{access_level_display} user created successfully.'
            messages.success(request, success_message)
            return redirect('/')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
    else:
        initial_password = generate_random_password()  # Generate the initial password
        form = PortalManagementForm(
            initial={'password1': initial_password, 'password2': initial_password})

        print(initial_password)

    return render(
        request=request,
        template_name="admin/hrs.html",
        context={"form": form, "initial_password": initial_password}
    )


logger = logging.getLogger(__name__)


@user_not_authenticated
def custom_login(request):
    error_messages = []
    
    if request.method == "POST":
        form = UserLoginForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.access_level == 5:
                   
                    try:
                        profile_update, created = ProfileUpdate.objects.get_or_create(
                            user=user, defaults={'password_changed': False})
                        if not profile_update.password_changed:
                            # Send activation link
                            sendActivationLink(request, user, user.email)
                            return redirect('users:staff_no')
                    except Exception as e:
                        logger.error(
                            f"Error checking or creating ProfileUpdate: {e}")

                if user.access_level != 5 or (user.access_level == 5 and profile_update.password_changed):
                    login(request, user)

                    if user.access_level in (1, 2, 3, 4):
                        try:
                            AdminAccessLog.objects.create(admin_user=user)
                        except Exception as e:
                            logger.error(
                                f"Error creating admin access log: {e}")
                    elif user.access_level == 0:
                        try:
                            UserAccessLog.objects.create(user=user)
                        except Exception as e:
                            logger.error(
                                f"Error creating user access log: {e}")

                    messages.success(
                        request, f"Hello {user.username}! You have been logged in.")
                    return redirect("/")
                else:
                    return redirect('users:staff_no')
            else:
                error_messages.append("Invalid username or password")
        else:
            for error in list(form.errors.values()):
                error_messages.append(error)

    form = UserLoginForm()
    return render(
        request=request,
        template_name="users/login.html",
        context={"form": form, "errors": error_messages}
    )


def sendActivationLink(request, user, to_email):
    mail_subject = 'Secure your user account.'
    message = render_to_string('users/secure_account.html', {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, from_email='hrm@careers.kengen.co.ke', to=[to_email], cc=['nelson.masibo@kenyaweb.com'],)
    email.extra_headers['Sender'] = 'nelson@kenyaweb.co.ke'

    
    if email.send():
        messages.success(
            request, f'Hello <b>{user},an email has been sent to {to_email}')
    else:
        messages.error(
            request, f'Problem sending the activation link to {to_email}, check if you typed it correctly.')


def profile(request, username):
    if request.method == 'POST':
        user = request.user
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            print("Form is valid")

            user_form = form.save()
            print("User form saved:", user_form)

            messages.success(
                request, f'{user_form}, Your profile has been updated!')
            return redirect('users:profile', user_form.username)

        for error in list(form.errors.values()):
            messages.error(request, error)

    user = get_user_model().objects.filter(username=username).first()
    if user:
        form = UserUpdateForm(instance=user)
        print("User instance:", user)
        return render(request, 'users/profile.html', context={'form': form})

    return redirect("/")


@login_required
def password_change(request):
    error_messages = []
    user = request.user

    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            old_password = form.cleaned_data['old_password']
            new_password1 = form.cleaned_data['new_password1']

            # Check if the old password matches the user's current password
            if not user.check_password(old_password):
                messages.error(request, "Your Current password is incorrect.")
                return redirect('users:password_change')

            # Check if the new password is the same as the old password
            if old_password == new_password1:
                messages.error(request, "Your new password must be different from the Current password.")
                return redirect('users:password_change')

            # Save the new password
            form.save()

            success_message = "Your password has been changed"

            if user.access_level == 5:
                try:
                    profile_update, created = ProfileUpdate.objects.get_or_create(
                        user=user, defaults={'password_changed': True})
                    if not profile_update.password_changed:
                        profile_update.password_changed = True
                        profile_update.save()
                except Exception as e:
                    error_messages.append(str(e))

            messages.success(request, success_message)
            return redirect('users:login')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    form = SetPasswordForm(user)
    return render(request, 'users/password_reset_confirm.html', {'form': form, "errors": error_messages})


@user_not_authenticated
def password_reset_request(request):
    errors = []
    
    if request.method == 'POST':
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data['email']
            user_id_number = form.cleaned_data['id_number']

            try:
                associated_user = get_user_model().objects.get(email__iexact=user_email)
            except get_user_model().DoesNotExist:
                associated_user = None

            if associated_user and associated_user.id_number == user_id_number:
                subject = _("Password Reset request")
                message = render_to_string("users/template_reset_password.html", {
                    'user': associated_user,
                    'domain': get_current_site(request).domain,
                    'uid': urlsafe_base64_encode(force_bytes(associated_user.pk)),
                    'token': account_activation_token.make_token(associated_user),
                    "protocol": 'https' if request.is_secure() else 'http'
                })

              
                email = EmailMessage(
                    subject,
                    message,
                    from_email='hrm@careers.kengen.co.ke',
                    to=[associated_user.email],
                    cc=['nelson.masibo@kenyaweb.com'],
                )

              
                email.extra_headers['Sender'] = 'nelson@kenyaweb.co.ke'

                if email.send():
                    return redirect('users:f_pass')
                else:
                    errors.append("Problem sending reset password email. Please retry.")
            else:
                errors.append("No user account found associated with the provided email or invalid ID")

    form = CustomPasswordResetForm()
    return render(
        request=request,
        template_name="users/password_reset.html",
        context={"form": form, "errors": errors}
    )


def passwordResetConfirm(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except User.DoesNotExist:
        user = None

    errors = []
    success_messages = []

    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                new_password = form.cleaned_data.get('new_password2')
                
                # Check if the new password is different from the old password
                if check_password(new_password, user.password):
                    errors.append("New password must be different from the old password.")
                else:
                    form.save()
                    success_messages.append("Your password has been set. You may log in now.")
                    return redirect('users:login')
            else:
                for error in list(form.errors.values()):
                    errors.append(error)

        form = SetPasswordForm(user)
        return render(request, 'users/password_reset_confirm.html', {'form': form, 'errors': errors, 'success_messages': success_messages})
    else:
        errors.append("Link is expired")

    errors.append('Something went wrong, redirecting back to Homepage')
    return render(request, 'your_homepage_template.html', {'errors': errors, 'success_messages': success_messages})


@login_required
def custom_logout(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("/")


def staff_no(request):
    # Retrieve user details from the URL parameters
    query_dict = QueryDict(request.META['QUERY_STRING'])
    user_id = query_dict.get('user_id')
    username = query_dict.get('username')

    # Retrieve all CustomUser objects
    custom_users = CustomUser.objects.all()

    return render(request, 'users/staff_no.html', {'staff': custom_users, 'user_id': user_id, 'username': username})


def create_access_level_5_user(request):
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST)

        if user_form.is_valid():
            # Generate a random password
            password = ''.join(random.choices(
                string.ascii_letters + string.digits, k=8))

            # Create the user account with access level 5
            user = user_form.save(commit=False)
            user.set_password(password)
            user.access_level = 5
            user.save()

            # Create a user instance in the resume model
            email_address = user.email
            full_name = f'{user.first_name} {user.last_name}'
            Resume.objects.create(
                email_address=email_address, full_name=full_name, user=user)

            # Send an activation email with the user details
            mail_subject = 'New account created on Kengen Career Portal.'
            message = render_to_string('users/new_account.html', {
                'user': user,
                'password': password,  # Pass the password to the template
                'domain': get_current_site(request).domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'protocol': 'https' if request.is_secure() else 'http',
            })
            to_email = user.email

            email = EmailMessage(mail_subject, message, to=[to_email])
            if email.send():
                messages.success(
                    request, f'Account Created successfully for {user.username}, and login details sent to {to_email}')
            else:
                messages.error(
                    request, f'Problem sending confirmation email to {to_email}, check if you typed it correctly.')

            return redirect('hr:kgn_staffs')  # Redirect to the staff_no view

    else:
        user_form = CustomUserCreationForm()

    return render(request, 'hr/create_staff.html', {'form': user_form})


def not_allowed(request):
    return render(request, 'users/permission_denied.html')


def f_pass(request):
    user = request.user
    return render(request, 'users/f_pass.html', {'user': user})


@login_required
def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.delete()
    return redirect('hr:system_users')

@login_required
def terms_acceptance(request, vacancy_id):
    user = request.user

    # Get or create UserAcceptedTerms instance for the user
    user_accepted_terms, created = UserAcceptedTerms.objects.get_or_create(
        user=user
    )

    # Toggle the 'accepted' field
    user_accepted_terms.accepted = not user_accepted_terms.accepted
    user_accepted_terms.save()

    # Redirect back to the 'job' view with the vacancy_id parameter
    return redirect('vacancies:job', vacancy_id=vacancy_id)

@login_required
def internal_terms_acceptance(request, vacancy_id):
    user = request.user

    # Get or create UserAcceptedTerms instance for the user
    user_accepted_terms, created = UserAcceptedTerms.objects.get_or_create(
        user=user
    )

    # Toggle the 'accepted' field
    user_accepted_terms.accepted = not user_accepted_terms.accepted
    user_accepted_terms.save()

    # Redirect back to the 'job' view with the vacancy_id parameter
    return redirect('vacancies:internal_detail', vacancy_id=vacancy_id)

@login_required
def internship_terms_acceptance(request, vacancy_id):
    user = request.user

    # Get or create UserAcceptedTerms instance for the user
    user_accepted_terms, created = UserAcceptedTerms.objects.get_or_create(
        user=user
    )

    # Toggle the 'accepted' field
    user_accepted_terms.accepted = not user_accepted_terms.accepted
    user_accepted_terms.save()

    # Redirect back to the 'job' view with the vacancy_id parameter
    return redirect('vacancies:internship', vacancy_id=vacancy_id)

@login_required
def attachment_terms_acceptance(request, vacancy_id):
    user = request.user

    # Get or create UserAcceptedTerms instance for the user
    user_accepted_terms, created = UserAcceptedTerms.objects.get_or_create(
        user=user
    )

    # Toggle the 'accepted' field
    user_accepted_terms.accepted = not user_accepted_terms.accepted
    user_accepted_terms.save()

    # Redirect back to the 'job' view with the vacancy_id parameter
    return redirect('vacancies:attachment', vacancy_id=vacancy_id)

