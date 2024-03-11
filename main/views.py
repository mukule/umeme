from django.shortcuts import render, redirect, get_object_or_404
from users.models import *
from .forms import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from vacancies.models import *
from datetime import *
import pycountry
from django.utils.dateparse import parse_date
from django.db.utils import IntegrityError
from django.utils import timezone
from users.decorators import *


@access_level_check(user_access_level=5, redirect_view_name='vacancies:internal')
def index(request):
    job_types = JobType.objects.exclude(name="Internal")
    print(job_types)

    return render(request, 'main/index.html', {'job_types': job_types})


def job_type_detail(request, pk):
    job_type = get_object_or_404(JobType, pk=pk)
    return render(request, 'main/job_type_detail.html', {'job_type': job_type})


@login_required
def user_profile(request):
    user = request.user
    print(user)

    if user.access_level == 5:
        try:
            profile_update = ProfileUpdate.objects.get(user=user)
            print(profile_update)
            if not profile_update.password_changed:
                return render(request, 'main/password_change_required.html')
        except ProfileUpdate.DoesNotExist:

            return render(request, 'main/password_change_required.html')

    try:
        resume = Resume.objects.get(user=user)
    except Resume.DoesNotExist:
        resume = None

    basic_education_instances = BasicEducation.objects.filter(user=user)

    further_studies_instances = FurtherStudies.objects.filter(user=user)

    certification_instances = Certification.objects.filter(user=user)

    membership_instances = Membership.objects.filter(user=user)

    work_experience_instances = WorkExperience.objects.filter(user=user)

    referee_instances = Referee.objects.filter(user=user)

    try:
        professional_summary = ProfessionalSummary.objects.get(user=user)
    except ProfessionalSummary.DoesNotExist:
        professional_summary = None

    return render(request, 'main/user_profile.html', {
        'user': user,
        'resume': resume,
        'basic_education_instances': basic_education_instances,
        'further_studies_instances': further_studies_instances,
        'certification_instances': certification_instances,
        'membership_instances': membership_instances,
        'work_experience_instances': work_experience_instances,
        'referee_instances': referee_instances,
        'professional_summary': professional_summary,
    })


@login_required
def staff(request):
    user = request.user
    resume = None
    further_studies = None
    memberships = None
    work_experiences = None
    certifications = None

    if user.access_level == 5:
        try:
            profile_update = ProfileUpdate.objects.get(user=user)
            if not profile_update.password_changed:
                return render(request, 'main/pass_change.html')
        except ProfileUpdate.DoesNotExist:
            # If no ProfileUpdate record exists, consider it as not changed.
            pass

        # Check if the user has a resume
        try:
            resume = Resume.objects.get(user=user)
        except Resume.DoesNotExist:
            # Handle the case where the user doesn't have a resume
            pass

        # Retrieve the user's further studies, memberships, work experiences, and certifications
        further_studies = FurtherStudies.objects.filter(user=user)
        memberships = Membership.objects.filter(user=user)
        work_experiences = WorkExperience.objects.filter(user=user)
        certifications = Certification.objects.filter(user=user)

    context = {
        'resume': resume,
        'further_studies_instances': further_studies,
        'membership_instances': memberships,
        'work_experience_instances': work_experiences,
        'certification_instances': certifications,
    }

    return render(request, 'main/staff.html', context)


@login_required
def basic_info(request, user_id):
    user = request.user

    try:
        user_info = Resume.objects.get(user=user)
    except Resume.DoesNotExist:
        user_info = None

    # Set initial_data for email and full_name based on the existence of user_info
    initial_data = {}

    if user_info is None:
        initial_data['email_address'] = user.email
        initial_data['full_name'] = user.get_full_name() or ''
        initial_data['id_number'] = user.id_number

    if request.method == 'POST':
        form = ResumeForm(request.POST, instance=user_info)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = user

            # Set disability_number to None if disability is False
            if not resume.disability:
                resume.disability_number = None

            # Set county to 'N/A' if country of birth is not Kenya
            if resume.country_of_birth != 'Kenya':
                resume.county = 'N/A'

            resume.save()
            messages.success(
                request, 'Your information has been updated successfully.')
            return redirect('main:user_profile')
        else:
            messages.error(
                request, 'There was an error in the form submission. Please check your inputs.')
    else:
        form = ResumeForm(instance=user_info, initial=initial_data)

    context = {
        'form': form,
    }

    return render(request, 'main/basic_info.html', context)


@login_required
def basic_academic(request):
    if request.method == 'POST':
        form = EducationalInformationForm(request.POST, request.FILES,)
        if form.is_valid():
            basic_education = form.save(commit=False)
            basic_education.user = request.user
            basic_education.save()
            return redirect('main:user_profile')
    else:
        form = EducationalInformationForm()

    context = {
        'form': form,
        'basic_education_instances': BasicEducation.objects.filter(user=request.user),
    }
    return render(request, 'main/basic_academic.html', context)


@login_required
def update_basic_academic(request, instance_id):
    user = request.user
    try:
        basic_education = BasicEducation.objects.get(user=user, pk=instance_id)
    except BasicEducation.DoesNotExist:
        return redirect('main:user_profile')

    if request.method == 'POST':
        form = EducationalInformationForm(
            request.POST, request.FILES, instance=basic_education)
        if form.is_valid():
            form.save()
            return redirect('main:user_profile')

    else:
        form = EducationalInformationForm(instance=basic_education)

    context = {
        'form': form,
    }
    return render(request, 'main/update_basic_academic.html', context)


@login_required
def delete_basic_academic(request, instance_id):
    instance = get_object_or_404(BasicEducation, pk=instance_id)
    instance.delete()
    return redirect('main:user_profile')


@login_required
def further_studies(request):
    user = request.user

    if request.method == 'POST':
        form = FurtherStudiesForm(request.POST, request.FILES)
        if form.is_valid():
            further_studies = form.save(commit=False)
            further_studies.user = user
            further_studies.save()

            if user.access_level == 5:
                # Redirect to a different view if access_level is 5
                return redirect('main:staff_profile')

            # Redirect to a success page or URL
            return redirect('main:user_profile')

    else:
        form = FurtherStudiesForm()

    context = {
        'form': form,
    }
    return render(request, 'main/further_studies.html', context)


@login_required
def update_further_studies(request, instance_id):
    user = request.user
    try:
        further_studies = FurtherStudies.objects.get(user=user, pk=instance_id)
    except FurtherStudies.DoesNotExist:
        return redirect('main:user_profile')

    if request.method == 'POST':
        form = FurtherStudiesForm(
            request.POST, request.FILES, instance=further_studies)
        if form.is_valid():
            form.save()
            if user.access_level == 5:
                # Redirect to a different view if access_level is 5
                return redirect('main:staff_profile')
            return redirect('main:user_profile')

    else:
        form = FurtherStudiesForm(instance=further_studies)

    context = {
        'form': form,
    }
    return render(request, 'main/update_further_studies.html', context)


@login_required
def delete_further_studies(request, instance_id):
    user = request.user
    instance = get_object_or_404(FurtherStudies, pk=instance_id)
    instance.delete()
    if user.access_level == 5:
        # Redirect to a different view if access_level is 5
        return redirect('main:staff_profile')
    return redirect('main:user_profile')


@login_required
def certification(request):
    user = request.user
    if request.method == 'POST':
        form = CertificationForm(request.POST, request.FILES)
        if form.is_valid():
            certification = form.save(commit=False)

            # Check if the name is not blank before saving
            if certification.name.strip():
                certification.user = request.user
                certification.save()

                if user.access_level == 5:
                    # Redirect to a different view if access_level is 5
                    return redirect('main:staff_profile')

                return redirect('main:user_profile')
            else:
                # Display an error message if the name is blank
                messages.error(
                    request, 'You cannot submit a Blank Certification')
    else:
        form = CertificationForm()

    context = {
        'form': form,
    }
    return render(request, 'main/certification.html', context)


@login_required
def update_certification(request, instance_id):
    user = request.user
    try:
        certification = Certification.objects.get(user=user, pk=instance_id)
    except Certification.DoesNotExist:
        if user.access_level == 5:
            # Redirect to a different view if access_level is 5
            return redirect('main:staff_profile')
        return redirect('main:user_profile')

    if request.method == 'POST':
        form = CertificationForm(
            request.POST, request.FILES, instance=certification)
        if form.is_valid():
            form.save()
            if user.access_level == 5:
                # Redirect to a different view if access_level is 5
                return redirect('main:staff_profile')
            return redirect('main:user_profile')

    else:
        form = CertificationForm(instance=certification)

    context = {
        'form': form,
    }
    return render(request, 'main/update_certification.html', context)


@login_required
def delete_certification(request, instance_id):
    user = request.user
    instance = get_object_or_404(Certification, pk=instance_id)
    instance.delete()
    if user.access_level == 5:
        # Redirect to a different view if access_level is 5
        return redirect('main:staff_profile')
    return redirect('main:user_profile')


@login_required
def membership(request):
    user = request.user

    if request.method == 'POST':
        form = MembershipForm(request.POST, request.FILES)
        if form.is_valid():
            membership = form.save(commit=False)

            if membership.membership_title.strip():
                membership.user = request.user
                membership.save()
                messages.success(request, 'Membership successfully submitted!')

                if user.access_level == 5:

                    return redirect('main:staff_profile')

                return redirect('main:user_profile')
            else:
                # Display an error message if the name is blank
                messages.error(request, 'Membership Title cannot be blank.')
        else:
            # If the form is not valid, display specific error messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

    else:
        form = MembershipForm()

    context = {
        'form': form,
    }
    return render(request, 'main/membership.html', context)


@login_required
def update_membership(request, instance_id):
    user = request.user
    try:
        membership = Membership.objects.get(user=user, pk=instance_id)
    except Membership.DoesNotExist:
        return redirect('main:user_profile')

    if request.method == 'POST':
        form = MembershipForm(request.POST, request.FILES, instance=membership)
        if form.is_valid():
            form.save()
            if user.access_level == 5:
                # Redirect to a different view if access_level is 5
                return redirect('main:staff_profile')
            return redirect('main:user_profile')

    else:
        form = MembershipForm(instance=membership)

    context = {
        'form': form,
    }
    return render(request, 'main/update_membership.html', context)


@login_required
def delete_membership(request, instance_id):
    user = request.user
    instance = get_object_or_404(Membership, pk=instance_id)
    instance.delete()
    if user.access_level == 5:
        # Redirect to a different view if access_level is 5
        return redirect('main:staff_profile')
    return redirect('main:user_profile')


@login_required
def work_experience(request):
    user = request.user
    if request.method == 'POST':
        form = WorkExperienceForm(request.POST)
        if form.is_valid():
            work_experience = form.save(commit=False)
            if work_experience.currently_working and work_experience.date_ended:
                messages.error(
                    request, "You cannot have an end date and be currently working here.")
            elif not work_experience.currently_working and (not work_experience.date_started or not work_experience.date_ended):
                messages.error(
                    request, "Please provide both start and end dates or check 'Currently Working Here'.")
            else:
                work_experience.user = request.user
                if work_experience.date_started and work_experience.date_ended:
                    delta = work_experience.date_ended - work_experience.date_started
                    years = delta.days // 365
                    # Calculate remaining months
                    months = (delta.days % 365) // 30
                    work_experience.years = years
                    work_experience.months = months
                elif work_experience.date_started and work_experience.currently_working:
                    delta = timezone.now().date() - work_experience.date_started
                    years = delta.days // 365
                    # Calculate remaining months
                    months = (delta.days % 365) // 30
                    work_experience.years = years
                    work_experience.months = months
                work_experience.save()
                if user.access_level == 5:
                    # Redirect to a different view if access_level is 5
                    return redirect('main:staff_profile')
                return redirect('main:user_profile')
    else:
        form = WorkExperienceForm()

    context = {
        'form': form,
    }
    return render(request, 'main/work_experience.html', context)


@login_required
def update_work_experience(request, instance_id):
    user = request.user
    try:
        work_experience = WorkExperience.objects.get(user=user, pk=instance_id)
    except WorkExperience.DoesNotExist:
        return redirect('main:user_profile')

    if request.method == 'POST':
        form = WorkExperienceForm(request.POST, instance=work_experience)
        if form.is_valid():
            new_work_experience = form.save(commit=False)
            if new_work_experience.currently_working and new_work_experience.date_ended:
                messages.error(
                    request, "You cannot have an end date and be currently working here.")
            elif not new_work_experience.currently_working and (not new_work_experience.date_started or not new_work_experience.date_ended):
                messages.error(
                    request, "Please provide both start and end dates or check 'Currently Working Here'.")
            else:
                if new_work_experience.date_started and new_work_experience.date_ended:
                    delta = new_work_experience.date_ended - new_work_experience.date_started
                    years = delta.days // 365
                    months = (delta.days % 365) // 30
                    new_work_experience.years = years
                    new_work_experience.months = months
                elif new_work_experience.date_started and new_work_experience.currently_working:
                    delta = timezone.now().date() - new_work_experience.date_started
                    years = delta.days // 365
                    months = (delta.days % 365) // 30
                    new_work_experience.years = years
                    new_work_experience.months = months
                new_work_experience.save()
                return redirect('main:user_profile')

    else:
        form = WorkExperienceForm(instance=work_experience)

    context = {
        'form': form,
    }
    return render(request, 'main/update_work_experience.html', context)


@login_required
def delete_work_experience(request, instance_id):
    user = request.user
    instance = get_object_or_404(WorkExperience, pk=instance_id)
    instance.delete()

    return redirect('main:user_profile')


@login_required
def referees(request):
    user = request.user
    referees_list = Referee.objects.filter(user=user)

    # Check if the user already has 3 referees
    if referees_list.count() >= 3:
        messages.error(request, "You can only have a maximum of 3 referees.")
        return redirect('main:user_profile')

    if request.method == 'POST':
        form = RefereeForm(request.POST)
        if form.is_valid():
            # Check again before saving to prevent exceeding the limit
            if referees_list.count() < 3:
                referee = form.save(commit=False)
                referee.user = user
                referee.save()
                return redirect('main:user_profile')
            else:
                messages.error(request, "You can only 3 referees required.")
    else:
        form = RefereeForm()

    context = {
        'form': form,
        'referees_list': referees_list,
    }
    return render(request, 'main/referees.html', context)


@login_required
def update_referee(request, instance_id):
    user = request.user
    try:
        referee = Referee.objects.get(user=user, pk=instance_id)
    except Referee.DoesNotExist:
        return redirect('main:user_profile')

    if request.method == 'POST':
        form = RefereeForm(request.POST, instance=referee)
        if form.is_valid():
            form.save()
            return redirect('main:user_profile')
    else:
        form = RefereeForm(instance=referee)

    context = {
        'form': form,
    }
    return render(request, 'main/update_referee.html', context)


@login_required
def delete_referee(request, instance_id):
    instance = get_object_or_404(Referee, pk=instance_id)
    instance.delete()
    return redirect('main:user_profile')


@login_required
def career_objective(request):
    user = request.user
    try:
        professional_summary = ProfessionalSummary.objects.get(user=user)
    except ProfessionalSummary.DoesNotExist:
        professional_summary = None

    if request.method == 'POST':
        form = ProfessionalSummaryForm(request.POST)
        if form.is_valid():
            if professional_summary:
                messages.error(
                    request, "You can only have one professional summary.")
                return redirect('main:user_profile')

            summary = form.save(commit=False)
            summary.user = user
            summary.save()
            return redirect('main:user_profile')
    else:
        form = ProfessionalSummaryForm(instance=professional_summary)

    context = {
        'form': form,
    }
    return render(request, 'main/professional_summary.html', context)


@login_required
def update_career_objective(request):
    user = request.user
    try:
        summary = ProfessionalSummary.objects.get(user=user)
    except ProfessionalSummary.DoesNotExist:
        return redirect('main:user_profile')

    if request.method == 'POST':
        form = ProfessionalSummaryForm(request.POST, instance=summary)
        if form.is_valid():
            form.save()
            return redirect('main:user_profile')
    else:
        form = ProfessionalSummaryForm(instance=summary)

    context = {
        'form': form,
    }
    return render(request, 'main/update_professional_summary.html', context)


@login_required
def delete_professional_summary(request):
    user = request.user
    try:
        summary = ProfessionalSummary.objects.get(user=user)
    except ProfessionalSummary.DoesNotExist:
        return redirect('main:user_profile')

    if request.method == 'POST':
        summary.delete()
        return redirect('main:user_profile')

    context = {
        'summary': summary,
    }
    return render(request, 'main/delete_professional_summary.html', context)


@login_required
def terms(request):

    user = request.user
    print(user)

    if user.access_level == 5:
        try:
            profile_update = ProfileUpdate.objects.get(user=user)
            print(profile_update)
            if not profile_update.password_changed:
                return render(request, 'main/pass_change.html')
        except ProfileUpdate.DoesNotExist:
            # If no ProfileUpdate record exists, consider it as not changed.
            return render(request, 'main/pass_change.html')
    # Assuming you want to display the first (and only) set of terms
    terms = Terms.objects.first()

    return render(request, 'main/terms.html', {'terms': terms})


@login_required
def update_educational_level(request):
    user = request.user

    # Try to get the user's resume
    try:
        resume = Resume.objects.get(user=user)
    except Resume.DoesNotExist:
        # If the user doesn't have a resume, create a new one
        resume = Resume(user=user)

    if request.method == 'POST':
        form = UpdateEducationalLevelForm(request.POST, instance=resume)
        if form.is_valid():
            form.save()
            # Redirect to a success page or URL
            return redirect('main:staff_profile')

    else:
        form = UpdateEducationalLevelForm(instance=resume)

    context = {
        'form': form,
        'resume': resume,
    }

    return render(request, 'main/edu_level.html', context)


def how(request):
    return render(request, 'main/how.html')
