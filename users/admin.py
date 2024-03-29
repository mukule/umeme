from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Resume)
admin.site.register(FieldOfStudy)
admin.site.register(EducationalLevel)
admin.site.register(Ethnicity)
admin.site.register(BasicEducation)
admin.site.register(FurtherStudiesCertification)
admin.site.register(Certification)
admin.site.register(FurtherStudies)
admin.site.register(CertifyingBody)
admin.site.register(WorkExperience)
admin.site.register(ProfessionalSummary)
admin.site.register(Membership)
admin.site.register(UserAccessLog)
admin.site.register(AdminAccessLog)
admin.site.register(ProfileUpdate)
admin.site.register(County)
admin.site.register(MaritalStatus)
admin.site.register(Gender)
admin.site.register(Class)
admin.site.register(Referee)