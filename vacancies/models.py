from django.db import models
from users.models import *


class JobDiscipline(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class JobType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    banner = models.ImageField(
        default='default/banner.jpg', upload_to='job_type_banners/', null=True, blank=True)
    icon = models.ImageField(default='default/icon.png',
                             upload_to='job_type_icons/', null=True, blank=True)

    def __str__(self):
        return self.name

    def vacancy_count(self):
        """
        Calculate and return the count of vacancies for this job type.
        """
        return self.vacancy_set.count()


class Vacancy(models.Model):
    job_type = models.ForeignKey(JobType, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=255)
    ref = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    position_responsibilities = models.TextField()
    reports_to = models.CharField(max_length=255)
    date_open = models.DateTimeField()  # Changed to DateTimeField
    date_close = models.DateTimeField()
    posts_needed = models.PositiveIntegerField()
    min_work_experience = models.PositiveIntegerField()
    min_educational_level = models.ForeignKey(
        EducationalLevel, on_delete=models.CASCADE)
    published = models.BooleanField(default=False)
    job_discipline = models.ForeignKey(
        JobDiscipline, on_delete=models.CASCADE, null=True)
    certifications_required = models.BooleanField(default=False)
    college_required = models.BooleanField(default=False)
    membership_required = models.BooleanField(default=False)
    created_by = models.CharField(max_length=255, null=True, blank=True)
    last_updated_by = models.CharField(max_length=255, null=True, blank=True)
    hired = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    @property
    def application_count(self):
        """
        Calculate and return the count of applications for this vacancy.
        """
        return self.application_set.count()


class Application(models.Model):
    applicant = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, null=True)
    application_date = models.DateTimeField(auto_now_add=True)
    qualify = models.BooleanField(default=False)
    shortlisted = models.BooleanField(default=False)
    work_experience = models.DecimalField(
        max_digits=5, decimal_places=2, null=True)
    highest_educational_level = models.CharField(max_length=255, null=True)
    reference_number = models.CharField(
        max_length=100, unique=True, blank=True, null=True)
    index = models.PositiveIntegerField(
        unique=True, editable=False, null=True, blank=True)
    years = models.PositiveIntegerField(default=0)
    months = models.PositiveIntegerField(default=0)
    disqualification_reason = models.CharField(max_length=255, null=True)

    def __str__(self):
        return f"{self.applicant.username} - {self.vacancy.title}"


class Terms(models.Model):
    EXTERNAL = 'external'
    INTERNAL = 'internal'

    TERM_TYPE_CHOICES = [
        (EXTERNAL, 'External'),
        (INTERNAL, 'Internal'),
    ]
    title = models.CharField(max_length=255, null=True, blank=True)
    banner = models.ImageField(
        default='default/banner.jpg', upload_to='terms_banners/', null=True, blank=True)
    text = models.TextField()
    term_type = models.CharField(
        max_length=10,
        choices=TERM_TYPE_CHOICES,
        default=INTERNAL,
    )

    def __str__(self):
        return f"Terms and Conditions ({self.get_term_type_display()})"


class UserAcceptedTerms(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)
    accepted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} accepted terms"


class ThanksMessage(models.Model):
    message = models.TextField()

    def __str__(self):
        return f"ThanksMessage {self.id}"
