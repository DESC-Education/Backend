from django.contrib import admin
from Profiles.models import (
    City,
    Skill,
    PhoneVerificationCode,
    University,
    Faculty,
    ProfileVerifyRequest,
    Specialty,
    StudentProfile,
    CompanyProfile


)



admin.site.register(City)
admin.site.register(Skill)
admin.site.register(PhoneVerificationCode)
admin.site.register(University)
admin.site.register(Faculty)
admin.site.register(ProfileVerifyRequest)
admin.site.register(Specialty)
admin.site.register(StudentProfile)
admin.site.register(CompanyProfile)
# Register your models here.
