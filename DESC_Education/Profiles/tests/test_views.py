from django.urls import reverse
import json
from django.utils import timezone
from rest_framework.test import APITestCase
from Users.models import (
    CustomUser
)
from tempfile import NamedTemporaryFile
from Profiles.models import (
    StudentProfile,
    University,
    ProfileVerifyRequest
)
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile


class StudentProfileView(APITestCase):

    @staticmethod
    def create_test_image():
        bts = BytesIO()
        img = Image.new("RGB", (100, 100))
        img.save(bts, 'jpeg')
        return SimpleUploadedFile("test.jpg", bts.getvalue())



    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="example@example.com",
            password="test123",
            role=CustomUser.STUDENT_ROLE,
            is_verified=True
        )
        self.company = CustomUser.objects.create_user(
            email="example2@example.com",
            password="test123",
            role=CustomUser.COMPANY_ROLE,
            is_verified=True
        )
        self.token = self.user.get_token()['accessToken']
        self.company_token = self.company.get_token()['accessToken']
        university = University.objects.first()
        self.example_data = {
            "firstName": "John",
            "lastName": "Doe",
            "description": "Student description",
            "phone": "+79991234567",
            "phoneVisibility": True,
            "emailVisibility": True,
            "telegramLink": "https://t.me/john_doe",
            "vkLink": "https://vk.com/john_doe",
            "timezone": 3,
            "formOfEducation": StudentProfile.FULL_TIME_EDUCATION,
            "speciality": "it",
            "admissionYear": 2020,
            "university": str(university.id),
            "studentCard": self.create_test_image()
        }


    def test_create_profile_200(self):
        example_data = self.example_data.copy()
        res = self.client.post(reverse("student_profile"),
                               data=example_data,
                               headers={"Authorization": f"Bearer {self.token}"},
                               )


        profile = StudentProfile.objects.first()

        expected_data = example_data
        expected_data["id"] = str(profile.id)
        expected_data["isVerified"] = False
        expected_data["logoImg"] = None
        expected_data["studentCard"] = profile.student_card.url


        res = json.loads(res.content)


        self.assertEqual(res.get("data").get("studentProfile"), expected_data)
        self.assertEqual(res.get("message"), "Профиль студента создан и отправлен на проверку!")

        v_request: ProfileVerifyRequest = ProfileVerifyRequest.objects.get(object_id=profile.id)
        self.assertEqual(v_request.profile.user, profile.user)
        self.assertEqual(v_request.status, v_request.PENDING)

    def test_duplicate_409(self, ):
        example_data = self.example_data.copy()
        example_data['studentCard'] = self.create_test_image()
        self.test_create_profile_200()
        res = self.client.post(reverse("student_profile"),
                               data=example_data,
                               headers={"Authorization": f"Bearer {self.token}"},
                               )


        self.assertEqual(res.data.get("message"), "Профиль с такими данными уже существует!")
        self.assertEqual(res.status_code, 409)

    def test_unathorized_401(self):
        res = self.client.post(reverse("student_profile"),
                               data=json.dumps({}),
                               content_type="application/json")

        self.assertEqual(res.data.get("detail"), 'Учетные данные не были предоставлены.')
        self.assertEqual(res.status_code, 401)

    def test_create_student_profile_to_company_403(self):
        res = self.client.post(reverse("student_profile"),
                               data=json.dumps({}),
                               headers={"Authorization": f"Bearer {self.company_token}"},
                               content_type="application/json"
                               )


        self.assertEqual(res.data.get("message"), 'Вы можете создать профиль студента только для студента!')
        self.assertEqual(res.status_code, 403)
