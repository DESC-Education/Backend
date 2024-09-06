from django.db.models.signals import post_save
from django.dispatch import receiver
from Profiles.models import StudentProfile
from Tasks.models import (
    Task,
    Solution
)




@receiver(post_save, sender=Solution)
def check_student_profile_level(sender, instance, **kwargs):
    if instance.status == Solution.COMPLETED:
        profile = instance.user.get_profile()
        profile.check_level()

