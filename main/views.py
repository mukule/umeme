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
from django.db.models import Q


@access_level_check(user_access_level=5, redirect_view_name='vacancies:internal')
def index(request):
    job_types = JobType.objects.exclude(name="Internal")
    print(job_types)

    return render(request, 'main/index.html', {'job_types': job_types})


def job_type_detail(request, pk):
    search_query = request.GET.get('search')
    job_type_filter = request.GET.get('vacancy_type')
    current_date = date.today()

    job_type = get_object_or_404(JobType, pk=pk)
    jobs = Vacancy.objects.filter(job_type=job_type)
    job_disciplines = JobDiscipline.objects.all()

    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if job_type_filter:
        jobs = jobs.filter(job_discipline__name=job_type_filter)

    context = {
        'job_type': job_type,
        'jobs': jobs,
        'job_disciplines': job_disciplines,
        'search_query': search_query,
        'selected_job_type': job_type_filter,
    }

    return render(request, 'main/job_type_detail.html', context)


@login_required
def job_detail(request, job_id):
    job = get_object_or_404(Vacancy, pk=job_id)

    user_accepted_terms, created = UserAcceptedTerms.objects.get_or_create(
        user=request.user
    )

    context = {
        'job': job,
        'terms': user_accepted_terms
    }

    return render(request, 'main/job_detail.html', context)


@login_required
def bio_info(request):
    job_types = JobType.objects.exclude(name="Internal")
    user = request.user
    print(user)

    if user.access_level == 5:
        try:
            profile_update = ProfileUpdate.objects.get(user=user)
            if not profile_update.password_changed:
                return render(request, 'main/password_change_required.html')
        except ProfileUpdate.DoesNotExist:

            return render(request, 'main/password_change_required.html')

    try:
        resume = Resume.objects.get(user=user)
    except Resume.DoesNotExist:
        resume = None

    basic_education_instance = BasicEducation.objects.filter(user=user).first()

    return render(request, 'main/bio_info.html', {
        'user': user,
        'resume': resume,
        'be': basic_education_instance
    })


@login_required
def high_school(request):
    user = request.user

    basic_education_instance = BasicEducation.objects.filter(user=user).first()
    further_studies_instance = FurtherStudies.objects.filter(user=user).first()

    return render(request, 'main/high_school.html', {
        'user': user,
        'be': basic_education_instance,
        'fs': further_studies_instance
    })


@login_required
def college(request):
    user = request.user

    further_studies_instance = FurtherStudies.objects.filter(user=user).all()
    certs_instance = Certification.objects.filter(user=user).all()

    return render(request, 'main/college.html', {
        'user': user,
        'fs': further_studies_instance,
        'certs': certs_instance

    })


@login_required
def certs(request):
    user = request.user

    certification_instance = Certification.objects.filter(user=user).all()
    further_studies_instance = FurtherStudies.objects.filter(user=user).all()
    membership_instance = Membership.objects.filter(user=user).all()

    return render(request, 'main/certs.html', {
        'user': user,
        'fs': further_studies_instance,
        'ms': membership_instance,
        'certs': certification_instance

    })


@login_required
def memberships(request):
    user = request.user

    membership_instance = Membership.objects.filter(user=user).all()
    certification_instance = Certification.objects.filter(user=user).all()
    wx_instance = WorkExperience.objects.filter(user=user).all()

    return render(request, 'main/memberships.html', {
        'user': user,
        'ms': membership_instance,
        'certs': certification_instance,
        'wx': wx_instance

    })


@login_required
def refs(request):
    user = request.user

    work_experience_instance = WorkExperience.objects.filter(user=user).all()
    certification_instance = Certification.objects.filter(user=user).all()
    referee_instance = Referee.objects.filter(user=user).all()

    return render(request, 'main/refs.html', {
        'user': user,
        'wx': work_experience_instance,
        'refs': referee_instance

    })


@login_required
def experience(request):
    user = request.user

    wx_instance = WorkExperience.objects.filter(user=user).all()
    certification_instance = Certification.objects.filter(user=user).all()
    referee_instance = Referee.objects.filter(user=user).all()

    return render(request, 'main/experience.html', {
        'user': user,
        'wx': wx_instance,
        'certs': certification_instance,
        'refs': referee_instance

    })

@login_required
def resume(request):
    user = request.user


    try:
        resume = Resume.objects.get(user=user)
    except Resume.DoesNotExist:
        resume = None
    
    basic_academic = BasicEducation.objects.filter(user=user).all()
    higher_education = FurtherStudies.objects.filter(user=user).order_by('-date_ended').all()
    wx_instance = WorkExperience.objects.filter(user=user).order_by('-date_ended').all()
    certification_instance = Certification.objects.filter(user=user).order_by('-date_attained').all()
    membership_instance = Membership.objects.filter(user=user).order_by('-date_joined').all()
    referee_instance = Referee.objects.filter(user=user).all()

    return render(request, 'main/resume.html', {
        'be':basic_academic,
        'he':higher_education,
        'resume':resume,
        'user': user,
        'wx': wx_instance,
        'certs': certification_instance,
        'ms':membership_instance,
        'refs': referee_instance

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
    job_types = JobType.objects.exclude(name="Internal")
    user = request.user

    try:
        user_info = Resume.objects.get(user=user)
    except Resume.DoesNotExist:
        user_info = None

    basic_education_instance = BasicEducation.objects.filter(user=user).first()
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
           
            if resume.country_of_residence != 'KE':
                resume.county = 'N/A'

            resume.save()
            messages.success(
                request, 'Your information has been updated successfully.')

            return redirect('main:bio_info')
           
        else:
            messages.error(
                request, 'There was an error in the form submission. Please check your inputs.')
    else:
        form = ResumeForm(instance=user_info, initial=initial_data)

    context = {
        'form': form,
        'job_types': job_types,
        'be': basic_education_instance
    }

    return render(request, 'main/basic_info.html', context)


@login_required
def basic_academic(request):
    job_types = JobType.objects.exclude(name="Internal")
    if request.method == 'POST':
        form = EducationalInformationForm(request.POST, request.FILES,)
        if form.is_valid():
            basic_education = form.save(commit=False)
            basic_education.user = request.user
            basic_education.save()
            messages.success(
                request, 'High School information updated successfully.')
            return redirect('main:high_school')
    else:
        form = EducationalInformationForm()

    context = {
        'form': form,
        'basic_education_instances': BasicEducation.objects.filter(user=request.user),
        'job_types': job_types
    }
    return render(request, 'main/basic_academic.html', context)


@login_required
def update_basic_academic(request, instance_id):
    job_types = JobType.objects.exclude(name="Internal")
    user = request.user

    try:
        basic_education = BasicEducation.objects.get(user=user, pk=instance_id)
    except BasicEducation.DoesNotExist:
        return redirect('main:basic_academic')

    further_studies_instance = FurtherStudies.objects.filter(user=user).first()

    # Save the current certificate file and remove it from the form instance
    current_certificate = basic_education.certificate
    # basic_education.certificate = None

    if request.method == 'POST':
        form = EducationalInformationForm(
            request.POST, request.FILES, instance=basic_education)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Your information has been updated successfully.')
            return redirect('main:high_school')
    else:
        # Include the 'certificate' field in the form instance
        form = EducationalInformationForm(instance=basic_education)

    context = {
        'form': form,
        'certificate': current_certificate,
        'job_types': job_types,
        'fs': further_studies_instance
    }
    return render(request, 'main/update_basic_academic.html', context)


@login_required
def delete_basic_academic(request, instance_id):
    instance = get_object_or_404(BasicEducation, pk=instance_id)
    instance.delete()
    return redirect('main:user_profile')


@login_required
def further_studies(request):
    job_types = JobType.objects.exclude(name="Internal")
    user = request.user

    certification_instance = Certification.objects.filter(user=user).first()
    basic_academic_instance = BasicEducation.objects.filter(user=user).first()
    further_studies_instance = FurtherStudies.objects.filter(user=user).all()

    if request.method == 'POST':
        form = FurtherStudiesForm(request.POST, request.FILES)
        if form.is_valid():
            further_studies = form.save(commit=False)
            further_studies.user = user
            further_studies.save()

            messages.success(
                request, 'Higher Education Details Added succesfully.')
            return redirect('main:college')

    else:
        form = FurtherStudiesForm()

    context = {
        'form': form,
        'job_types': job_types,
        'cert': certification_instance,
        'be': basic_academic_instance,
        'fs': further_studies_instance
    }
    return render(request, 'main/further_studies.html', context)


@login_required
def update_further_studies(request, instance_id):
    job_types = JobType.objects.exclude(name="Internal")
    user = request.user
    try:
        further_studies = FurtherStudies.objects.get(user=user, pk=instance_id)
    except FurtherStudies.DoesNotExist:
        return redirect('main:basic_academic')
    basic_education_instance = BasicEducation.objects.filter(user=user).first()
    certification_instance = Certification.objects.filter(user=user).first()

    if request.method == 'POST':
        form = FurtherStudiesForm(
            request.POST, request.FILES, instance=further_studies)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Your information has been updated successfully.')
            
            return redirect('main:college')

    else:
        form = FurtherStudiesForm(instance=further_studies)

    context = {
        'form': form,
        'job_types': job_types,
        'be': basic_education_instance,
        'cert': certification_instance
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
    job_types = JobType.objects.exclude(name="Internal")
    user = request.user

    further_studies_instance = FurtherStudies.objects.filter(user=user).all()
    membership_instance = Membership.objects.filter(user=user).all()
    if request.method == 'POST':
        form = CertificationForm(request.POST, request.FILES)
        if form.is_valid():
            certification = form.save(commit=False)

            # Check if the name is not blank before saving
            if certification.name.strip():
                certification.user = request.user
                certification.save()

                messages.success(
                    request, 'Your Certification Added succesfully')
                
                return redirect('main:certs')
               
            else:
                # Display an error message if the name is blank
                messages.error(
                    request, 'You cannot submit a Blank Certification')
    else:
        form = CertificationForm()

    context = {
        'form': form,
        'job_types': job_types,
        'fs': further_studies_instance,
        'ms': membership_instance
    }
    print(job_types)
    return render(request, 'main/certification.html', context)


@login_required
def update_certification(request, instance_id):
    job_types = JobType.objects.exclude(name="Internal")
    user = request.user
    try:
        certification = Certification.objects.get(user=user, pk=instance_id)
    except Certification.DoesNotExist:
        if user.access_level == 5:
            # Redirect to a different view if access_level is 5
            return redirect('main:certification')
        return redirect('main:certification')

    further_studies_instance = FurtherStudies.objects.filter(user=user).first()
    membership_instance = Membership.objects.filter(user=user).first()

    if request.method == 'POST':
        form = CertificationForm(
            request.POST, request.FILES, instance=certification)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Your information has been updated successfully.')
           
            return redirect('main:certs')

    else:
        form = CertificationForm(instance=certification)

    context = {
        'form': form,
        'job_types': job_types,
        'fs': further_studies_instance,
        'ms': membership_instance
    }
    print(job_types)
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
    job_types = JobType.objects.exclude(name="Internal")
    user = request.user

    certification_instance = Certification.objects.filter(user=user).all()
    refees_instance = Referee.objects.filter(user=user).all()

    if request.method == 'POST':
        form = MembershipForm(request.POST, request.FILES)
        if form.is_valid():
            membership = form.save(commit=False)

            if membership.membership_title.strip():
                membership.user = request.user
                membership.save()
                messages.success(
                    request, 'Membership Cetifications added succesfully')
                
                return redirect('main:memberships')
                
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
        'job_types': job_types,
        'certs': certification_instance,
        'refs': refees_instance
    }
    return render(request, 'main/membership.html', context)


@login_required
def update_membership(request, instance_id):

    job_types = JobType.objects.exclude(name="Internal")
    user = request.user
    try:
        membership = Membership.objects.get(user=user, pk=instance_id)
    except Membership.DoesNotExist:
        return redirect('main:membership')

    certification_instance = Certification.objects.filter(user=user).first()
    work_experience_instance = WorkExperience.objects.filter(user=user).first()

    if request.method == 'POST':
        form = MembershipForm(request.POST, request.FILES, instance=membership)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Your information has been updated successfully.')
            
            return redirect('main:memberships')
            
    else:
        form = MembershipForm(instance=membership)

    context = {
        'form': form,
        'job_types': job_types,
        'cert': certification_instance,
        'wx': work_experience_instance
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
    job_types = JobType.objects.exclude(name="Internal")
    user = request.user

    membership_instance = Membership.objects.filter(user=user).first()
    referee_instance = Referee.objects.filter(user=user).first()

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

                return redirect('main:experience')
    else:
        form = WorkExperienceForm()

    context = {
        'form': form,
        'job_types': job_types,
        'ms': membership_instance,
        'refs': referee_instance
    }
    return render(request, 'main/work_experience.html', context)


@login_required
def update_work_experience(request, instance_id):
    job_types = JobType.objects.exclude(name="Internal")
    user = request.user
    try:
        work_experience = WorkExperience.objects.get(user=user, pk=instance_id)
    except WorkExperience.DoesNotExist:
        return redirect('main:work_experience')

    membership_instance = Membership.objects.filter(user=user).first()
    referee_instance = Referee.objects.filter(user=user).first()

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
                return redirect('main:experience')

    else:
        form = WorkExperienceForm(instance=work_experience)

    context = {
        'form': form,
        'job_types': job_types,
        'ms': membership_instance,
        'refs': referee_instance
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
    job_types = JobType.objects.exclude(name="Internal")
    user = request.user
    referees_list = Referee.objects.filter(user=user)
    work_experience_instance = WorkExperience.objects.filter(user=user).first()

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
                return redirect('main:refs')
            else:
                messages.error(request, "You can only 3 referees required.")
    else:
        form = RefereeForm()

    context = {
        'form': form,
        'referees_list': referees_list,
        'job_types': job_types,
        'wx': work_experience_instance
    }
    return render(request, 'main/referees.html', context)


@login_required
def update_referee(request, instance_id):
    job_types = JobType.objects.exclude(name="Internal")
    user = request.user
    try:
        referee = Referee.objects.get(user=user, pk=instance_id)
    except Referee.DoesNotExist:
        return redirect('main:referees')

    work_experience_instance = WorkExperience.objects.filter(user=user).first()

    if request.method == 'POST':
        form = RefereeForm(request.POST, instance=referee)
        if form.is_valid():
            form.save()
            return redirect('main:refs')
    else:
        form = RefereeForm(instance=referee)

    context = {
        'form': form,
        'job_types': job_types,
        'wx': work_experience_instance
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
    job_types = JobType.objects.exclude(name="Internal")

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

    return render(request, 'main/terms.html', {'terms': terms, 'job_types': job_types})


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
