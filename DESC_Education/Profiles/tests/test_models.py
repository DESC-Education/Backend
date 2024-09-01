import random
from django.test import TestCase
from Profiles.models import (
    StudentProfile,
    CompanyProfile,
    BaseProfile,
    ProfileVerifyRequest,
    CustomUser,

)




class ProfileModelTest(TestCase):
    def create_v_requests(self, profile):

        pass

    def create_profile(self, model):
        profiles = {
            StudentProfile: CustomUser.STUDENT_ROLE,
            CompanyProfile: CustomUser.COMPANY_ROLE,
        }

        user: CustomUser = CustomUser.objects.create_user(
            email=f"example{random.randint(1,99999)}@example.com",
            password="test123",
            role=profiles[model],
            is_verified=True)



        profile: BaseProfile = model.objects.get(user=user)
        return profile

    def setUp(self):
        self.student_profile = self.create_profile(StudentProfile)
        self.company_profile = self.create_profile(CompanyProfile)

    def abstract_model_test(self, profile: BaseProfile):
        self.assertEqual(profile.verification, profile.NOT_VERIFIED)

        v_request: ProfileVerifyRequest = ProfileVerifyRequest.objects.create(profile=profile)
        self.assertEqual(v_request.status, v_request.PENDING)

        profile_verification_status = profile.get_verification_status()
        self.assertEqual(profile_verification_status.get('status'), profile.ON_VERIFICATION)

        v_request_3: ProfileVerifyRequest = ProfileVerifyRequest.objects.create(
            profile=profile, status=v_request.REJECTED, comment="example comment")
        self.assertEqual(v_request_3.status, v_request.REJECTED)

        profile_verification_status = profile.get_verification_status()
        self.assertEqual(profile_verification_status, {
            "status": profile.REJECTED,
            "comment": "example comment"
        })

        v_request_2: ProfileVerifyRequest = ProfileVerifyRequest.objects.create(
            profile=profile, status=v_request.APPROVED)
        self.assertEqual(v_request_2.status, v_request.APPROVED)

        profile_verification_status = profile.get_verification_status()
        self.assertEqual(profile_verification_status.get('status'), profile.VERIFIED)
        self.assertEqual(profile.verification, profile.VERIFIED)




    def test_verification_status(self):
        self.abstract_model_test(self.company_profile)
        self.abstract_model_test(self.student_profile)



