import logging
from .models import Staff
import re
from django.shortcuts import render, redirect
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


def is_system_admin(user):
    return user.is_superuser or (user.access_level == 'system admin')


def not_authorized(request):
    return render(
        request,
        template_name="admin/not_authorized.html"
    )


# Create your views here.
@user_not_authenticated
def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            activateEmail(request, user, form.cleaned_data.get('email'))
            return redirect('/')

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
    mail_subject = 'Activate your user account.'
    message = render_to_string('users/template_activate_account.html', {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Dear <b>{user}</b>, please go to you email <b>{to_email}</b> inbox and click on \
            received activation link to confirm and complete the registration. <b>Note:</b> Check your spam folder.')
    else:
        messages.error(
            request, f'Problem sending confirmation email to {to_email}, check if you typed it correctly.')


def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(
            request, 'Thank you for your email confirmation. Now you can login your account.')
        return redirect('users:login')
    else:
        messages.error(request, 'Activation link is invalid!')

    return redirect('/')


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

        messages.success(request, 'Gracious, Change Password Now and Apply .')
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
    if request.method == "POST":
        form = UserLoginForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.access_level == 5:
                    # Check if the user's password has been changed in ProfileUpdate
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
                    # Log in users with access level other than 5 and level 5 with changed password
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
                messages.error(request, "Invalid username or password")
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    form = UserLoginForm()
    return render(
        request=request,
        template_name="users/login.html",
        context={"form": form}
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
    email = EmailMessage(mail_subject, message, to=[to_email])
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
    user = request.user
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your password has been changed")

            if user.access_level == 5:
                try:
                    profile_update, created = ProfileUpdate.objects.get_or_create(
                        user=user, defaults={'password_changed': True})
                    if not profile_update.password_changed:
                        profile_update.password_changed = True
                        profile_update.save()
                except Exception as e:
                    messages.error(
                        request, f"Error updating password change status: {e}")

            return redirect('users:login')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    form = SetPasswordForm(user)
    return render(request, 'users/password_reset_confirm.html', {'form': form})


@user_not_authenticated
def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data['email']
            associated_user = get_user_model().objects.filter(Q(email=user_email)).first()
            if associated_user:
                subject = "Password Reset request"
                message = render_to_string("users/template_reset_password.html", {
                    'user': associated_user,
                    'domain': get_current_site(request).domain,
                    'uid': urlsafe_base64_encode(force_bytes(associated_user.pk)),
                    'token': account_activation_token.make_token(associated_user),
                    "protocol": 'https' if request.is_secure() else 'http'
                })
                email = EmailMessage(subject, message, to=[
                                     associated_user.email])
                if email.send():
                    messages.success(request,
                                     """
                        <h2>Password reset sent</h2><hr>
                        <p>
                            We've emailed you instructions for setting your password, if an account exists with the email you entered. 
                            You should receive them shortly.<br>If you don't receive an email, please make sure you've entered the address 
                            you registered with, and check your spam folder.
                        </p>
                        """
                                     )
                else:
                    messages.error(
                        request, "Problem sending reset password email, <b>SERVER PROBLEM</b>")

            return redirect('/')

    form = PasswordResetForm()
    return render(
        request=request,
        template_name="users/password_reset.html",
        context={"form": form}
    )


def passwordResetConfirm(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(
                    request, "Your password has been set. You may go ahead and <b>log in </b> now.")
                return redirect('users:login')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)

        form = SetPasswordForm(user)
        return render(request, 'users/password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, "Link is expired")

    messages.error(
        request, 'Something went wrong, redirecting back to Homepage')
    return redirect("/")


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