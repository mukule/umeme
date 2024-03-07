from django.db import models
from users.models import *



class JobDiscipline(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Vacancy(models.Model):
    VACANCY_TYPES = (
        ('Internal', 'Internal'),
        ('Careers', 'Career'),
        ('Internship', 'Internship'),
        ('Attachment', 'Attachment'),
    )

    vacancy_type = models.CharField(max_length=20, choices=VACANCY_TYPES)
    title = models.CharField(max_length=255)
    ref = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    position_responsibilities = models.TextField()
    reports_to = models.CharField(max_length=255)
    date_open = models.DateField()
    date_close = models.DateField()
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
        max_length=20, unique=True, blank=True, null=True)
    index = models.PositiveIntegerField(
        unique=True, editable=False, null=True, blank=True)
    years = models.PositiveIntegerField(default=0)
    months = models.PositiveIntegerField(default=0)
    disqualification_reason = models.CharField(max_length=255, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:  # Only on creation, not on updates
            max_index = Application.objects.aggregate(
                models.Max('index'))['index__max']
            self.index = (max_index or 0) + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.applicant.username} - {self.vacancy.title}"


class Terms(models.Model):
    text = models.TextField()

    def __str__(self):
        return "Terms and Conditions"


class UserAcceptedTerms(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)
    accepted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} accepted terms"
