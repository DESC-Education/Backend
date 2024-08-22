import random

import rest_framework.generics
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
    CompanyProfile,
    University,
    ProfileVerifyRequest,
    File,
    Skill,
    City,
    Faculty
)
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from Profiles.serializers import (
    CreateCompanyProfileSerializer,
    CreateStudentProfileSerializer,
    UniversitySerializer,
    SkillSerializer,
    FacultySerializer,
)


class CreateProfileViewTest(APITestCase):

    @staticmethod
    def create_test_image():
        bts = BytesIO()
        img = Image.new("RGB", (100, 100))
        img.save(bts, 'jpeg')
        return SimpleUploadedFile(f"test_{random.randint(1, 25)}.jpg", bts.getvalue())

    def get_skils_ids(self):
        skills_ids = []

        skills = Skill.objects.all()

        for i in skills:
            skills_ids.append(i.id)

        return skills_ids, SkillSerializer(skills, many=True).data

    def setUp(self):
        self.maxDiff = None
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
        self.admin = CustomUser.objects.create_user(
            email="example3@example.com",
            password="test123",
            role=CustomUser.ADMIN_ROLE,
            is_verified=True
        )
        self.admin_token = self.admin.get_token()['accessToken']
        self.token = self.user.get_token()['accessToken']
        self.company_token = self.company.get_token()['accessToken']
        self.university = University.objects.first()
        self.faculty = Faculty.objects.first()
        skills = self.get_skils_ids()
        skills_ids = skills[0]
        self.skills = list(skills[1])
        self.student_example_data = {
            "firstName": "John",
            "lastName": "Doe",
            "description": "Student description",
            "phoneVisibility": True,
            "emailVisibility": True,
            "telegramLink": "https://t.me/john_doe",
            "vkLink": "https://vk.com/john_doe",
            "timezone": 3,
            "formOfEducation": StudentProfile.FULL_TIME_EDUCATION,
            "speciality": "it",
            'educationProgram': StudentProfile.BACHELOR,
            "admissionYear": 2020,
            "university": str(self.university.id),
            "faculty": str(self.faculty.id),
            "files": [self.create_test_image()],
            "skills_ids": skills_ids
        }

        self.company_example_data = {
            "firstName": "John",
            "lastName": "Doe",
            "description": "Student description",
            "phoneVisibility": True,
            "emailVisibility": True,
            "telegramLink": "https://t.me/john_doe",
            "vkLink": "https://vk.com/john_doe",
            "timezone": 3,
            "companyName": "Test Company",
            'linkToCompany': "https://link.com/",
            'files': [self.create_test_image() for _ in range(6)]
        }

    def test_create_student_profile_200(self):
        res = self.client.post(reverse('profile_create'),
                               data=self.student_example_data,
                               headers={"Authorization": f"Bearer {self.token}"})

        profile: StudentProfile = StudentProfile.objects.first()

        expected_data = self.student_example_data
        expected_data["id"] = str(profile.id)
        expected_data["isVerified"] = False
        expected_data["logoImg"] = None
        expected_data["phone"] = None
        files = expected_data.pop('files')
        skills_ids = expected_data.pop('skills_ids')
        expected_skill_names = set()
        for i in self.skills:
            expected_skill_names.add(i.get('name'))
        expected_data['skills'] = expected_skill_names
        expected_data['formOfEducation'] = profile.get_form_of_education_display()
        expected_data['educationProgram'] = profile.get_education_program_display()
        expected_data['university'] = dict(UniversitySerializer(self.university).data)
        faculty = dict(FacultySerializer(self.faculty).data)
        faculty['university'] = str(faculty.get('university'))
        expected_data['faculty'] = faculty


        result = json.loads(res.content).get("data").get("studentProfile")
        res_skills_names = set()
        for i in result.get("skills"):
            res_skills_names.add(i.get('name'))
        result['skills'] = res_skills_names
        self.assertEqual(result, expected_data)
        self.assertEqual(len(files), profile.verification_files.count())
        self.assertEqual(profile.skills.count(), len(skills_ids))
        self.assertEqual(res.status_code, 200)
        v_request: ProfileVerifyRequest = ProfileVerifyRequest.objects.first()

        self.assertEqual(v_request.profile, profile)
        self.assertEqual(v_request.status, v_request.PENDING)

    def test_create_company_profile_200(self):
        res = self.client.post(reverse('profile_create'),
                               data=self.company_example_data,
                               format='multipart',
                               headers={"Authorization": f"Bearer {self.company_token}"})

        profile: CompanyProfile = CompanyProfile.objects.first()

        expected_data = self.company_example_data.copy()
        expected_data["id"] = str(profile.id)
        expected_data["isVerified"] = False
        expected_data["logoImg"] = None
        expected_data["phone"] = None
        files = expected_data.pop('files')

        self.assertEqual(len(files), profile.verification_files.count())
        self.assertEqual(json.loads(res.content).get("data").get("companyProfile"), expected_data)
        self.assertEqual(CreateCompanyProfileSerializer(profile).data, expected_data)
        self.assertEqual(res.status_code, 200)

    def test_student_duplicate_405(self, ):
        example_data = self.student_example_data.copy()
        example_data['studentCard'] = self.create_test_image()

        self.test_create_student_profile_200()
        res = self.client.post(reverse("profile_create"),
                               data=example_data,
                               headers={"Authorization": f"Bearer {self.token}"},
                               )

        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.data.get('message'), 'Профиль еще на проверке')

    def test_student_rejected_200(self, ):
        example_data = self.student_example_data.copy()
        example_data['firstName'] = "newFIrstName"

        self.test_create_student_profile_200()
        ProfileVerifyRequest.objects.filter(object_id=StudentProfile.objects.first().id) \
            .update(status=ProfileVerifyRequest.REJECTED)

        res = self.client.post(reverse("profile_create"),
                               data=example_data,
                               headers={"Authorization": f"Bearer {self.token}"},
                               )

        profile = StudentProfile.objects.first()

        expected_data = example_data
        expected_data["id"] = str(profile.id)
        expected_data["isVerified"] = False
        expected_data["logoImg"] = None
        expected_data["phone"] = None
        expected_data.pop('files')
        expected_data.pop('skills_ids')
        expected_skill_names = set()
        for i in self.skills:
            expected_skill_names.add(i.get('name'))
        expected_data['skills'] = expected_skill_names
        expected_data['university'] = dict(UniversitySerializer(self.university).data)
        expected_data['formOfEducation'] = profile.get_form_of_education_display()
        expected_data['educationProgram'] = profile.get_education_program_display()
        faculty = dict(FacultySerializer(self.faculty).data)
        faculty['university'] = str(faculty.get('university'))
        expected_data['faculty'] = faculty

        result = json.loads(res.content).get("data").get("studentProfile")
        res_skills_names = set()
        for i in result.get("skills"):
            res_skills_names.add(i.get('name'))
        result['skills'] = res_skills_names
        self.assertEqual(result, expected_data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data.get('message'), 'Профиль создан и отправлен на проверку!')


    def test_company_rejected_200(self, ):
        example_data = self.company_example_data.copy()
        example_data['firstName'] = "newFIrstName"

        self.test_create_company_profile_200()
        ProfileVerifyRequest.objects.filter(object_id=CompanyProfile.objects.first().id) \
            .update(status=ProfileVerifyRequest.REJECTED)

        res = self.client.post(reverse("profile_create"),
                               data=example_data,
                               headers={"Authorization": f"Bearer {self.company_token}"},
                               )

        profile = CompanyProfile.objects.first()

        expected_data = example_data
        expected_data["id"] = str(profile.id)
        expected_data["isVerified"] = False
        expected_data["logoImg"] = None
        expected_data["phone"] = None
        expected_data.pop("files")


        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data.get('message'), 'Профиль создан и отправлен на проверку!')
        self.assertEqual(json.loads(res.content).get("data").get("companyProfile"), expected_data)

    def test_company_not_verified_405(self, ):
        example_data = self.company_example_data.copy()

        self.test_create_company_profile_200()
        res = self.client.post(reverse("profile_create"),
                               data=example_data,
                               headers={"Authorization": f"Bearer {self.company_token}"},
                               )

        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.data.get('message'), 'Профиль еще на проверке')

    def test_company_verified_405(self, ):
        example_data = self.company_example_data.copy()
        self.test_create_company_profile_200()
        profile = CompanyProfile.objects.first()
        profile.is_verified = True
        profile.save()
        res = self.client.post(reverse("profile_create"),
                               data=example_data,
                               headers={"Authorization": f"Bearer {self.company_token}"},
                               )

        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.data.get('message'), 'Профиль уже подтвержден')

    def test_create_admin_profile_403(self):
        res = self.client.post(reverse('profile_create'),
                               data=self.student_example_data,
                               headers={"Authorization": f"Bearer {self.admin_token}"})

        self.assertEqual(res.status_code, 403)
        self.assertEqual(res.data.get('message'), 'Вы можете создать профиль только для студента или компании!')


class GetMyProfileTest(APITestCase):

    def setUp(self):
        self.maxDiff = None
        self.user = CustomUser.objects.create_user(
            email="example@example.com",
            password="test123",
            role=CustomUser.STUDENT_ROLE,
            is_verified=True
        )
        self.token = self.user.get_token()["accessToken"]

    def test_get_profile_200(self):
        res = self.client.get(reverse('profile_my'),
                              headers={"Authorization": f"Bearer {self.token}"})

        profile = StudentProfile.objects.get()
        expected_data = dict(CreateStudentProfileSerializer(profile).data)
        expected_data['skills'] = []

        self.assertEqual(json.loads(res.content).get('data').get('studentProfile'), expected_data)
        self.assertEqual(res.status_code, 200)


class GetProfileTest(APITestCase):
    @staticmethod
    def create_test_image():
        bts = BytesIO()
        img = Image.new("RGB", (100, 100))
        img.save(bts, 'jpeg')
        return SimpleUploadedFile(f"test_{random.randint(1, 25)}.jpg", bts.getvalue())

    def get_skils_ids(self):
        skills_ids = []

        skills = Skill.objects.all()

        for i in skills:
            skills_ids.append(i.id)

        return skills_ids, SkillSerializer(skills, many=True).data

    def setUp(self):
        self.maxDiff = None
        self.user = CustomUser.objects.create_user(
            email="example@example.com",
            password="test123",
            role=CustomUser.STUDENT_ROLE,
            is_verified=True
        )

        self.token = self.user.get_token()["accessToken"]
        self.university = University.objects.first()
        skills = self.get_skils_ids()
        self.skills = skills[1]
        skills_ids = skills[0]
        self.faculty = Faculty.objects.first()
        self.student_example_data = {
            "firstName": "John",
            "lastName": "Doe",
            "description": "Student description",
            "phoneVisibility": False,
            "emailVisibility": True,
            "telegramLink": "https://t.me/john_doe",
            "vkLink": "https://vk.com/john_doe",
            "timezone": 3,
            "formOfEducation": StudentProfile.FULL_TIME_EDUCATION,
            "speciality": "it",
            'educationProgram': StudentProfile.BACHELOR,
            "admissionYear": 2020,
            "university": str(self.university.id),
            "faculty": str(self.faculty.id),
            "files": [self.create_test_image()],
            "skills_ids": skills_ids
        }

    def test_get_profile_200(self):
        res = self.client.post(reverse('profile_create'),
                               data=self.student_example_data,
                               headers={"Authorization": f"Bearer {self.token}"})

        profile = StudentProfile.objects.first()
        profile.is_verified = True
        profile.save()
        res = self.client.get(reverse("profile_get", kwargs={"pk": str(self.user.id)})
                              )

        expected_data = self.student_example_data.copy()
        expected_data["id"] = str(profile.id)
        expected_data["isVerified"] = True
        expected_data["logoImg"] = None
        expected_data["email"] = profile.user.email
        expected_data.pop('emailVisibility')
        expected_data.pop('phoneVisibility')

        expected_data.pop('files')
        expected_data.pop('skills_ids')
        expected_skill_names = set()
        for i in self.skills:
            expected_skill_names.add(i.get('name'))
        expected_data['skills'] = expected_skill_names
        expected_data['university'] = dict(UniversitySerializer(self.university).data)
        faculty = dict(FacultySerializer(self.faculty).data)
        faculty['university'] = str(faculty.get('university'))
        expected_data['faculty'] = faculty
        expected_data['formOfEducation'] = profile.get_form_of_education_display()
        expected_data['educationProgram'] = profile.get_education_program_display()

        result = json.loads(res.content).get("data").get("studentProfile")

        res_skills_names = set()
        for i in result.get("skills"):
            res_skills_names.add(i.get('name'))
        result['skills'] = res_skills_names
        self.assertEqual(result, expected_data)
        self.assertEqual(res.status_code, 200)

    def test_get_invalid_profile_404(self):
        user_id = list(str(self.user.id))
        f = user_id[0]
        user_id[0] = user_id[-1]
        user_id[-1] = f
        user_id = ''.join(user_id)

        res = self.client.get(reverse("profile_get", kwargs={"pk": user_id}))

        self.assertEqual(json.loads(res.content), {'message': 'Профиль не найден'})
        self.assertEqual(res.status_code, 404)


class UniversitiesListTest(APITestCase):
    def setUp(self):
        University.objects.all().delete()
        city = City.objects.first()
        University.objects.create(name='Школа', city_id=city.id)
        University.objects.create(name='Университет', city_id=city.id)
        University.objects.create(name='Высший университет', city_id=city.id)

    def test_get(self):
        res = self.client.get(reverse('universities_list'), {'search': "Школа"})

        self.assertEqual(res.data[0].get('name'), 'Школа')
        self.assertEqual(res.status_code, 200)

    def test_get_not_found(self):
        res = self.client.get(reverse('universities_list'), {'search': "Школа11"})

        self.assertEqual(res.data, [])
        self.assertEqual(res.status_code, 200)


class SkillListTest(APITestCase):
    def setUp(self):
        Skill.objects.all().delete()
        Skill.objects.create(name='Python', is_verified=True)
        Skill.objects.create(name='C#', is_verified=True)
        Skill.objects.create(name='Illustrator', is_verified=True)

    def test_get(self):
        res = self.client.get(reverse('skills_list'), {'search': "ill"})

        self.assertEqual(res.data[0].get('name'), 'Illustrator')
        self.assertEqual(res.status_code, 200)

    def test_get_not_found(self):
        res = self.client.get(reverse('universities_list'), {'search': "Школа11"})

        self.assertEqual(res.data, [])
        self.assertEqual(res.status_code, 200)


class CitiesTest(APITestCase):
    def setUp(self):
        City.objects.all().delete()
        City.objects.create(name='Красноярск')
        City.objects.create(name='Новгород')
        City.objects.create(name='Москва')

    def test_get(self):
        res = self.client.get(reverse('cities_list'), {'search': "Красно"})

        self.assertEqual(res.data[0].get('name'), 'Красноярск')
        self.assertEqual(res.status_code, 200)

    def test_get_not_found(self):
        res = self.client.get(reverse('cities_list'), {'search': "Школа11"})

        self.assertEqual(res.data, [])
        self.assertEqual(res.status_code, 200)
