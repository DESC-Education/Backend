from django.contrib import admin
from Users.models import CustomUser, VerificationCode

admin.site.register(CustomUser)
admin.site.register(VerificationCode)

# Register your models here.
