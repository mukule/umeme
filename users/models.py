from django.contrib.auth.models import AbstractUser
from django.db import models
import os
from django_countries.fields import CountryField
from datetime import *
from django.db.models import F, Max


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    ACCESS_LEVEL_CHOICES = (
        (0, 'Job Seeker'),
        (1, 'System Admin'),
        (2, 'HR'),
        (3, 'HR Interns'),
        (4, 'HR Attachments'),
        (5, 'staffs'),
    )
    FUNCTION_CHOICES = (
        (0, 'No Previllages'),
        (1, 'Hr-General'),
        (2, 'Hr-Post Jobs(Internal/External)'),
        (3, 'Hr-Post Internship/Attachment'),
        (4, 'Hr-Publsh Jobs(Internal/External)'),
        (5, 'Hr-Publish Internship/Attachment'),
        (6, 'Hr-Edit Jobs(Internal/External)'),
        (7, 'Hr-Edit Internship/Attachment'),
        (8, 'Hr-Delete Jobs(Internal/External)'),
        (9, 'Hr-Delete Internship/Attachment'),
        (10, 'ICT'),

    )

    staff_no = models.CharField(max_length=20, unique=True, null=True)
    trials = models.PositiveIntegerField(default=4)
    is_restricted = models.BooleanField(default=False)

    access_level = models.PositiveIntegerField(
        choices=ACCESS_LEVEL_CHOICES,
        default=0,
    )
    function = models.PositiveIntegerField(
        choices=FUNCTION_CHOICES,
        default=0,
    )

    id_number = models.PositiveIntegerField(
        unique=True, blank=True, null=True)

    def image_upload_to(self, filename):
        return os.path.join('Users', self.username, filename)

    profile = models.ImageField(
        default='default/user.jpg',
        upload_to=image_upload_to
    )

    def __str__(self):
        return f"{self.id}"


class ProfileUpdate(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    password_changed = models.BooleanField(default=False)

    def __str__(self):
        return f"Profile Update for {self.user.username}"


class Staff(models.Model):
    staff_no = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, null=True)

    def __str__(self):
        return self.staff_no


class UserAccessLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.timestamp}"


class AdminAccessLog(models.Model):
    admin_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.admin_user.username} - {self.timestamp}"


class Ethnicity(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class EducationalLevel(models.Model):
    name = models.CharField(max_length=255)
    index = models.PositiveIntegerField(unique=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.pk:  # Only on creation, not on updates
            max_index = EducationalLevel.objects.aggregate(Max('index'))[
                'index__max']
            self.index = (max_index or 0) + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['index']


class FieldOfStudy(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class CertifyingBody(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Certificate(models.Model):
    name = models.CharField(max_length=255)
    certifying_body = models.ForeignKey(
        CertifyingBody, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name


class MaritalStatus(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Gender(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class County(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Counties"


class Resume(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    # Basic Information
    full_name = models.CharField(max_length=255, blank=True, null=True)
    email_address = models.EmailField(blank=True, null=True, unique=True)
    phone = models.CharField(max_length=10, blank=True, null=True, unique=True)
    id_number = models.PositiveIntegerField(
        unique=True, blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    country_of_birth = CountryField(blank=True, null=True)
    country_of_residence = CountryField(blank=True, null=True)
    county_of_birth = models.CharField(
        max_length=255, blank=True, null=True)  # Changed field
    county_of_residence = models.CharField(
        max_length=255, blank=True, null=True)
    ethnicity = models.ForeignKey(
        Ethnicity, on_delete=models.SET_NULL, blank=True, null=True)

    religeon = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=50, blank=True, null=True)
    DISABILITY_CHOICES = (
        (True, 'Yes'),
        (False, 'No'),
    )
    disability = models.BooleanField(
        choices=DISABILITY_CHOICES, default=False, blank=True, null=True)
    disability_number = models.CharField(max_length=20, blank=True, null=True)

    marital_status = models.CharField(max_length=50, blank=True, null=True)

    educational_level = models.ForeignKey(
        EducationalLevel, on_delete=models.SET_NULL, blank=True, null=True)
    field_of_study = models.ForeignKey(
        FieldOfStudy, on_delete=models.SET_NULL, blank=True, null=True)
    date_registered = models.DateTimeField(auto_now_add=True)

    age = models.PositiveIntegerField(blank=True, null=True, editable=False)

    @property
    def calculate_age(self):
        if self.dob:
            today = date.today()
            birth_date = self.dob
            age = today.year - birth_date.year - \
                ((today.month, today.day) < (birth_date.month, birth_date.day))
            return age
        return None

    def save(self, *args, **kwargs):
        self.age = self.calculate_age
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Resume for {self.user.username}"


class BasicEducation(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='basic_education')
    name_of_the_school = models.CharField(
        max_length=255, blank=True, null=True)
    certification_choices = (
        ('KCSE', 'Kenya Certificate of Secondary Education (KCSE)'),
        ('KCPE', 'Kenya Certificate of Primary Education (KCPE)'),
    )
    certification = models.CharField(
        max_length=10, choices=certification_choices, default='KCSE', blank=True, null=True)
    date_started = models.DateField(blank=True, null=True)
    date_ended = models.DateField(blank=True, null=True)
    grade_attained = models.CharField(max_length=10, blank=True, null=True)
    certificate = models.FileField(
        upload_to='certificates/{user_id}/{basic_education_id}/', blank=True, null=True)

    def __str__(self):
        return f"Basic Education for {self.user.username}"


class FurtherStudiesCertification(models.Model):
    certification_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.certification_name}"


class FurtherStudies(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='further_studies')
    institution_name = models.CharField(max_length=255, blank=True, null=True)
    certifications = models.ForeignKey(
        EducationalLevel, on_delete=models.SET_NULL, blank=True, null=True)
    course_undertaken = models.CharField(max_length=100, blank=True, null=True)
    date_started = models.DateField(blank=True, null=True)
    date_ended = models.DateField(blank=True, null=True)
    grade = models.CharField(max_length=100, blank=True, null=True)
    certificate = models.FileField(
        upload_to='certificates/{user_id}/{further_studies_id}/', blank=True, null=True)

    def __str__(self):
        return self.institution_name


class Membership(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                             related_name='memberships', blank=True, null=True)
    membership_title = models.CharField(max_length=255, blank=True, null=True)
    membership_number = models.CharField(max_length=50, blank=True, null=True)
    membership_body = models.CharField(max_length=255, blank=True, null=True)
    date_joined = models.DateField(blank=True, null=True)
    certificate = models.FileField(
        upload_to='certificates/{user_id}/memberships/', blank=True, null=True)

    def __str__(self):
        return self.membership_title


class WorkExperience(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                             related_name='work_experiences', blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    position = models.CharField(max_length=255, blank=True, null=True)
    date_started = models.DateField(blank=True, null=True)
    date_ended = models.DateField(blank=True, null=True)
    company_address = models.CharField(max_length=255, blank=True, null=True)
    company_phone = models.CharField(max_length=20, blank=True, null=True)
    responsibilities = models.TextField(blank=True, null=True)
    currently_working = models.BooleanField(default=False)
    years = models.PositiveIntegerField(blank=True, null=True)
    months = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return self.company_name


class Certification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                             related_name='certifications', blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    certifying_body = models.ForeignKey(
        CertifyingBody, on_delete=models.CASCADE, blank=True, null=True)
    date_attained = models.DateField(blank=True, null=True)
    certificate = models.FileField(
        upload_to='certificates/', blank=True, null=True)

    def __str__(self):
        return self.name


class Referee(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='referees')
    full_name = models.CharField(max_length=255)
    organization = models.CharField(max_length=255)
    designation = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return self.full_name


class ProfessionalSummary(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name='professional_summary')
    career_objective = models.TextField()

    def __str__(self):
        return f"{self.user.username}"


class Class(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Log(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='logs')
    activity = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.activity} - {self.timestamp}"
