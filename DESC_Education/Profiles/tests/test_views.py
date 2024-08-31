import random
import uuid

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
    Faculty,
    Specialty,
    PhoneVerificationCode
)
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from Profiles.serializers import (
    CreateCompanyProfileSerializer,
    StudentProfileSerializer,
    UniversitySerializer,
    SkillSerializer,
    FacultySerializer,
    SpecialtySerializer,
    GetStudentProfileSerializer,
    GetCompanyProfileSerializer,
    CitySerializer
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
        user_profile = StudentProfile.objects.get(user=self.user)
        user_profile.phone = '+77777777777'
        user_profile.save()
        self.company = CustomUser.objects.create_user(
            email="example2@example.com",
            password="test123",
            role=CustomUser.COMPANY_ROLE,
            is_verified=True
        )
        company_profile = CompanyProfile.objects.get(user=self.company)
        company_profile.phone = '+77777777777'
        company_profile.save()
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
        self.city = City.objects.first()
        self.faculty = Faculty.objects.first()
        skills = self.get_skils_ids()
        skills_ids = skills[0]
        self.skills = list(skills[1])
        self.specialty = Specialty.objects.first()
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
            "admissionYear": 2020,
            "university": str(self.university.id),
            "specialty": str(self.specialty.id),
            "faculty": str(self.faculty.id),
            "city": str(self.city.id),
            "files": [self.create_test_image()],
            "skills": skills_ids
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
            "city": str(self.city.id),
            'files': [self.create_test_image() for _ in range(6)],
            "skills": skills_ids
        }

    def test_create_student_profile_201(self):
        res = self.client.post(reverse('profile_create'),
                               data=self.student_example_data,
                               headers={"Authorization": f"Bearer {self.token}"})

        profile: StudentProfile = StudentProfile.objects.first()

        expected_data = self.student_example_data
        expected_data["id"] = str(profile.id)
        expected_data["verification"] = "on_verification"
        expected_data["logoImg"] = None
        expected_data["phone"] = '+77777777777'
        files = expected_data.pop('files')
        skills = expected_data.pop('skills')
        expected_skill_names = set()
        for i in self.skills:
            expected_skill_names.add(i.get('name'))
        expected_data['skills'] = expected_skill_names
        expected_data['formOfEducation'] = profile.get_form_of_education_display()
        expected_data['university'] = dict(UniversitySerializer(self.university).data)
        expected_data['specialty'] = dict(SpecialtySerializer(self.specialty).data)
        expected_data['city'] = dict(CitySerializer(self.city).data)

        faculty = dict(FacultySerializer(self.faculty).data)
        faculty['university'] = faculty.get('university')
        expected_data['faculty'] = faculty

        result = dict(res.data)
        res_skills_names = set()
        for i in result.get("skills"):
            res_skills_names.add(i.get('name'))
        result['skills'] = res_skills_names
        self.assertEqual(result, expected_data)
        self.assertEqual(len(files), profile.verification_files.count())
        self.assertEqual(profile.skills.count(), len(skills))
        self.assertEqual(res.status_code, 201)
        v_request: ProfileVerifyRequest = ProfileVerifyRequest.objects.first()

        self.assertEqual(v_request.profile, profile)
        self.assertEqual(v_request.status, v_request.PENDING)

    def test_create_company_profile_201(self):
        res = self.client.post(reverse('profile_create'),
                               data=self.company_example_data,
                               format='multipart',
                               headers={"Authorization": f"Bearer {self.company_token}"})

        profile: CompanyProfile = CompanyProfile.objects.first()

        expected_data = self.company_example_data.copy()
        expected_data["id"] = str(profile.id)
        expected_data["verification"] = "on_verification"
        expected_data["logoImg"] = None
        expected_data["phone"] = '+77777777777'
        expected_data['city'] = dict(CitySerializer(self.city).data)
        skills = expected_data.pop('skills')
        expected_skill_names = set()
        for i in self.skills:
            expected_skill_names.add(i.get('name'))
        expected_data['skills'] = expected_skill_names
        files = expected_data.pop('files')

        result = dict(res.data)
        res_skills_names = set()
        for i in result.get("skills"):
            res_skills_names.add(i.get('name'))
        result['skills'] = res_skills_names
        self.assertEqual(result, expected_data)

        self.assertEqual(len(files), profile.verification_files.count())

        self.assertEqual(res.status_code, 201)

    def test_student_duplicate_405(self, ):
        example_data = self.student_example_data.copy()
        example_data['studentCard'] = self.create_test_image()

        self.test_create_student_profile_201()
        res = self.client.post(reverse("profile_create"),
                               data=example_data,
                               headers={"Authorization": f"Bearer {self.token}"},
                               )

        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.data.get('message'), 'Профиль еще на проверке')

    def test_student_rejected_200(self, ):
        example_data = self.student_example_data.copy()
        example_data['firstName'] = "newFIrstName"

        self.test_create_student_profile_201()
        ProfileVerifyRequest.objects.filter(object_id=StudentProfile.objects.first().id) \
            .update(status=ProfileVerifyRequest.REJECTED)

        res = self.client.post(reverse("profile_create"),
                               data=example_data,
                               headers={"Authorization": f"Bearer {self.token}"},
                               )

        profile = StudentProfile.objects.first()

        expected_data = example_data
        expected_data["id"] = str(profile.id)
        expected_data["verification"] = "on_verification"
        expected_data["logoImg"] = None
        expected_data["phone"] = '+77777777777'
        expected_data.pop('files')
        expected_data.pop('skills')
        expected_skill_names = set()
        for i in self.skills:
            expected_skill_names.add(i.get('name'))
        expected_data['skills'] = expected_skill_names
        expected_data['university'] = dict(UniversitySerializer(self.university).data)
        expected_data['specialty'] = dict(SpecialtySerializer(self.specialty).data)
        expected_data['city'] = dict(CitySerializer(self.city).data)
        faculty = dict(FacultySerializer(self.faculty).data)
        faculty['university'] = faculty.get('university')
        expected_data['faculty'] = faculty
        expected_data['formOfEducation'] = profile.get_form_of_education_display()

        result = dict(res.data)
        res_skills_names = set()
        for i in result.get("skills"):
            res_skills_names.add(i.get('name'))
        result['skills'] = res_skills_names
        self.assertEqual(result, expected_data)
        self.assertEqual(res.status_code, 201)

    def test_company_rejected_200(self, ):
        example_data = self.company_example_data.copy()
        example_data['firstName'] = "newFIrstName"

        self.test_create_company_profile_201()
        ProfileVerifyRequest.objects.filter(object_id=CompanyProfile.objects.first().id) \
            .update(status=ProfileVerifyRequest.REJECTED)

        res = self.client.post(reverse("profile_create"),
                               data=example_data,
                               headers={"Authorization": f"Bearer {self.company_token}"},
                               )

        profile = CompanyProfile.objects.first()

        expected_data = example_data
        expected_data["id"] = str(profile.id)
        expected_data["verification"] = "on_verification"
        expected_data["logoImg"] = None
        expected_data["phone"] = '+77777777777'
        expected_data['city'] = dict(CitySerializer(self.city).data)
        skills = expected_data.pop('skills')
        expected_skill_names = set()
        for i in self.skills:
            expected_skill_names.add(i.get('name'))
        expected_data['skills'] = expected_skill_names
        expected_data.pop("files")


        result = dict(res.data)
        res_skills_names = set()
        for i in result.get("skills"):
            res_skills_names.add(i.get('name'))
        result['skills'] = res_skills_names

        self.assertEqual(result, expected_data)
        self.assertEqual(res.status_code, 201)


    def test_company_not_verified_405(self, ):
        example_data = self.company_example_data.copy()

        self.test_create_company_profile_201()
        res = self.client.post(reverse("profile_create"),
                               data=example_data,
                               headers={"Authorization": f"Bearer {self.company_token}"},
                               )

        self.assertEqual(res.status_code, 405)
        self.assertEqual(res.data.get('message'), 'Профиль еще на проверке')

    def test_company_verified_405(self, ):
        example_data = self.company_example_data.copy()
        self.test_create_company_profile_201()
        profile = CompanyProfile.objects.first()
        profile.verification = profile.VERIFIED
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
        expected_data = dict(StudentProfileSerializer(profile).data)
        expected_data['skills'] = []

        self.assertEqual(dict(res.data), expected_data)
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
        user_profile = StudentProfile.objects.get(user=self.user)
        user_profile.phone = '+77777777777'
        user_profile.save()

        self.token = self.user.get_token()["accessToken"]
        self.university = University.objects.first()
        self.specialty = Specialty.objects.first()
        skills = self.get_skils_ids()
        self.skills = skills[1]
        skills_ids = skills[0]
        self.faculty = Faculty.objects.first()
        self.city = City.objects.first()
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
            "admissionYear": 2020,
            "university": str(self.university.id),
            "specialty": str(self.specialty.id),
            "faculty": str(self.faculty.id),
            "city": str(self.city.id),
            "files": [self.create_test_image()],
            "skills": skills_ids
        }

    def test_get_profile_200(self):
        res = self.client.post(reverse('profile_create'),
                               data=self.student_example_data,
                               headers={"Authorization": f"Bearer {self.token}"})

        profile = StudentProfile.objects.first()
        profile.verification = profile.VERIFIED
        profile.save()
        res = self.client.get(reverse("profile_get", kwargs={"pk": str(self.user.id)}))



        expected_data = self.student_example_data.copy()
        expected_data["id"] = str(profile.id)
        expected_data["verification"] = "verified"
        expected_data["logoImg"] = None
        expected_data["email"] = profile.user.email
        expected_data.pop('emailVisibility')
        expected_data.pop('phoneVisibility')

        expected_data.pop('files')
        expected_data.pop('skills')
        expected_skill_names = set()
        for i in self.skills:
            expected_skill_names.add(i.get('name'))
        expected_data['skills'] = expected_skill_names
        expected_data['university'] = dict(UniversitySerializer(self.university).data)
        expected_data['specialty'] = dict(SpecialtySerializer(self.specialty).data)
        faculty = dict(FacultySerializer(self.faculty).data)
        faculty['university'] = faculty.get('university')
        expected_data['city'] = dict(CitySerializer(self.city).data)
        expected_data['faculty'] = faculty
        expected_data['formOfEducation'] = profile.get_form_of_education_display()

        result = dict(res.data)

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

        self.assertEqual(res.data.get('results')[0].get('name'), 'Школа')
        self.assertEqual(res.status_code, 200)

    def test_get_not_found(self):
        res = self.client.get(reverse('universities_list'), {'search': "Школа11"})

        self.assertEqual(res.data.get('results'), [])
        self.assertEqual(res.status_code, 200)


class SkillListTest(APITestCase):
    def setUp(self):
        Skill.objects.all().delete()
        Skill.objects.create(name='Python')
        Skill.objects.create(name='C#')
        Skill.objects.create(name='Illustrator')

    def test_get(self):
        res = self.client.get(reverse('skills_list'), {'search': "ill"})

        self.assertEqual(res.data.get('results')[0].get('name'), 'Illustrator')
        self.assertEqual(res.status_code, 200)

    def test_get_not_found(self):
        res = self.client.get(reverse('universities_list'), {'search': "Школа11"})

        self.assertEqual(res.data.get('results'), [])
        self.assertEqual(res.status_code, 200)


class CitiesListTest(APITestCase):
    def setUp(self):
        City.objects.all().delete()
        City.objects.create(name='Красноярск')
        City.objects.create(name='Новгород')
        City.objects.create(name='Москва')

    def test_get(self):
        res = self.client.get(reverse('cities_list'), {'search': "Красно"})

        self.assertEqual(res.data.get('results')[0].get('name'), 'Красноярск')
        self.assertEqual(res.status_code, 200)

    def test_get_not_found(self):
        res = self.client.get(reverse('cities_list'), {'search': "Школа11"})

        self.assertEqual(res.data.get('results'), [])
        self.assertEqual(res.status_code, 200)


class FacultiesListTest(APITestCase):

    def setUp(self):
        Faculty.objects.all().delete()
        University.objects.all().delete()
        self.university = University.objects.create(name='University', city=City.objects.first())
        self.university2 = University.objects.create(name='University2', city=City.objects.first())
        Faculty.objects.create(name='Факультет информатики', university_id=self.university.id)
        Faculty.objects.create(name='Факультет экономики', university_id=self.university.id)
        Faculty.objects.create(name='Факультет менеджмента', university_id=self.university.id)

        Faculty.objects.create(name='Факультет древологии', university_id=self.university2.id)

        self.url = reverse('faculties_list')

    def test_get_faculties(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data.get('results')), 4)

    def test_filter__by_name(self):
        response = self.client.get(self.url, {'search': 'эконом'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data.get('results')), 1)
        self.assertEqual(response.data.get('results')[0]['name'], "Факультет экономики")

    def test_filter__by_university_id(self):
        response = self.client.get(self.url, {'universityId': self.university2.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data.get('results')), 1)
        self.assertEqual(response.data.get('results')[0]['name'], "Факультет древологии")

    def test_filter_and_search_combined(self):
        response = self.client.get(self.url, {'universityId': self.university.id, 'search': 'информа'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data.get('results')), 1)
        self.assertEqual(response.data.get('results')[0]['name'], "Факультет информатики")


class SpecialtiesListTest(APITestCase):
    def setUp(self):
        Specialty.objects.all().delete()

        Specialty.objects.create(name='Информатика', code='1.0.1', type=Specialty.BACHELOR)
        Specialty.objects.create(name='Математика', code='1.0.2', type=Specialty.SPECIALTY)
        Specialty.objects.create(name='Программирование', code='1.0.3', type=Specialty.MAGISTRACY)

        self.url = reverse('specialties_list')

    def test_filter_specialties_by_name(self):
        response = self.client.get(self.url, {'search': 'раммирова'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data.get('results')), 1)
        self.assertEqual(response.data.get('results')[0]['name'], "Программирование")

    def test_filter_specialties_by_code(self):
        response = self.client.get(self.url, {'search': '1.0.2'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data.get('results')), 1)
        self.assertEqual(response.data.get('results')[0]['name'], "Математика")


class ChangeLogoImgViewTest(APITestCase):
    @staticmethod
    def create_test_image():
        bts = BytesIO()
        img = Image.new("RGB", (100, 100))
        img.save(bts, 'jpeg')
        return SimpleUploadedFile(f"test_{random.randint(1, 25)}.jpg", bts.getvalue())

    def setUp(self):
        self.user = CustomUser.objects.create_user(password='testuser',
                                                   email='testuser@example.com',
                                                   role=CustomUser.STUDENT_ROLE)
        self.token = self.user.get_token()['accessToken']
        self.image = self.create_test_image()

    def test_change_logo_200(self):
        res = self.client.post(reverse('logo_change'), {'logo': self.image},
                               HTTP_AUTHORIZATION='Bearer ' + self.token)
        profile = StudentProfile.objects.get(user=self.user)

        self.assertEqual(f'/api/media/users/{profile.user.id}/logo/{self.image}', profile.logo_img.url)
        self.assertEqual(res.status_code, 200)


class SendPhoneCodeViewTest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(password='testuser',
                                                   email='testuser@example.com',
                                                   role=CustomUser.STUDENT_ROLE)
        self.token = self.user.get_token()['accessToken']

    def test_send_v_code_200(self):
        res = self.client.post(reverse('send_phone_code'), {'phone': '+79991234567'},
                               HTTP_AUTHORIZATION='Bearer ' + self.token)

        p = PhoneVerificationCode.objects.first()

        self.assertEqual(p.phone, '+79991234567')
        self.assertEqual(res.data.get('message'), 'Код подтверждения отправлен')
        self.assertEqual(res.status_code, 200)

    def test_incorrect_phone_405(self):
        res = self.client.post(reverse('send_phone_code'), {'phone': '+793a456979'},
                               HTTP_AUTHORIZATION='Bearer ' + self.token)

        self.assertEqual(res.data.get('message'), 'Неверный формат номера телефона')
        self.assertEqual(res.status_code, 406)

    def test_delay_409(self):
        self.test_send_v_code_200()
        res = self.client.post(reverse('send_phone_code'), {'phone': '+79991234567'},
                               HTTP_AUTHORIZATION='Bearer ' + self.token)

        self.assertEqual(res.data.get('message'), 'Код подтверждения уже был отправлен.'
                                                  ' Пожалуйста, повторите попытку позже.')
        self.assertEqual(res.status_code, 409)

    def test_duplicate_phone(self):
        self.test_send_v_code_200()

        p = PhoneVerificationCode.objects.first()
        p.is_used = True
        p.save()

        res = self.client.post(reverse('send_phone_code'), {'phone': '+79991234567'},
                               HTTP_AUTHORIZATION='Bearer ' + self.token)

        self.assertEqual(res.data.get('message'), 'Данный номер телефона уже привязан!')
        self.assertEqual(res.status_code, 404)


class SetPhoneView(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(password='testuser',
                                                   email='testuser@example.com',
                                                   role=CustomUser.STUDENT_ROLE)
        self.token = self.user.get_token()['accessToken']

        PhoneVerificationCode.objects.create(user=self.user, code=123456,
                                             phone='+79876543210',
                                             is_used=False)

        self.company = CustomUser.objects.create_user(password='testuser',
                                                      email='testuser2@example.com',
                                                      role=CustomUser.COMPANY_ROLE)
        self.company_token = self.company.get_token()['accessToken']

        PhoneVerificationCode.objects.create(user=self.company, code=123456,
                                             phone='+71876543210',
                                             is_used=False)

    def test_student_set_phone_200(self):
        res = self.client.post(reverse('set_phone'), {'phone': '+79876543210', 'code': 101010},
                               HTTP_AUTHORIZATION='Bearer ' + self.token)

        self.assertEqual(res.data.get('phone'), '+79876543210')
        self.assertEqual(res.status_code, 200)

    def test_student_incorrect_phone_404(self):
        res = self.client.post(reverse('set_phone'), {'phone': '+7876543210', 'code': 101010},
                               HTTP_AUTHORIZATION='Bearer ' + self.token)

        self.assertEqual(res.data.get('message'), 'Неверный номер телефона или код')
        self.assertEqual(res.status_code, 404)

    def test_company_set_phone_200(self):
        res = self.client.post(reverse('set_phone'), {'phone': '+71876543210', 'code': 101010},
                               HTTP_AUTHORIZATION='Bearer ' + self.company_token)

        self.assertEqual(res.data.get('phone'), '+71876543210')
        self.assertEqual(res.status_code, 200)


class EditProfileViewTest(APITestCase):
    def setUp(self):
        self.student = CustomUser.objects.create_user(
            email='example@example.com',
            password='password',
            role=CustomUser.STUDENT_ROLE
        )

        self.student_token = self.student.get_token()['accessToken']

        self.company = CustomUser.objects.create_user(
            email='company@example.com',
            password='password',
            role=CustomUser.COMPANY_ROLE
        )
        self.company_token = self.company.get_token()['accessToken']

    def test_edit_student_profile_200(self):
        res = self.client.post(reverse('profile_edit'),
                               {'vkLink': 'https://vk.com'},
                               HTTP_AUTHORIZATION='Bearer ' + self.student_token)

        self.assertEqual(dict(res.data).get('vkLink'), 'https://vk.com')
        self.assertEqual(res.status_code, 200)

        res = self.client.post(reverse('profile_edit'),
                               {'telegramLink': 'https://tg.com'},
                               HTTP_AUTHORIZATION='Bearer ' + self.student_token)

        self.assertEqual(dict(res.data).get('telegramLink'), 'https://tg.com')
        self.assertEqual(res.status_code, 200)

        res = self.client.post(reverse('profile_edit'),
                               {'emailVisibility': False},
                               HTTP_AUTHORIZATION='Bearer ' + self.student_token)

        self.assertEqual(dict(res.data).get('emailVisibility'),
                         False)
        self.assertEqual(res.status_code, 200)

        res = self.client.post(reverse('profile_edit'),
                               {'phoneVisibility': False},
                               HTTP_AUTHORIZATION='Bearer ' + self.student_token)

        self.assertEqual(dict(res.data).get('phoneVisibility'),
                         False)
        self.assertEqual(res.status_code, 200)


    def test_edit_company_profile_200(self):
        res = self.client.post(reverse('profile_edit'),
                               {'vkLink': 'https://vk.com'},
                               HTTP_AUTHORIZATION='Bearer ' + self.company_token)



        self.assertEqual(res.data.get('vkLink'), 'https://vk.com')
        self.assertEqual(res.status_code, 200)

        res = self.client.post(reverse('profile_edit'),
                               {'telegramLink': 'https://tg.com'},
                               HTTP_AUTHORIZATION='Bearer ' + self.company_token)

        self.assertEqual(dict(res.data).get('telegramLink'), 'https://tg.com')
        self.assertEqual(res.status_code, 200)

        res = self.client.post(reverse('profile_edit'),
                               {'emailVisibility': False},
                               HTTP_AUTHORIZATION='Bearer ' + self.company_token)

        self.assertEqual(dict(res.data).get('emailVisibility'),
                         False)
        self.assertEqual(res.status_code, 200)

        res = self.client.post(reverse('profile_edit'),
                               {'phoneVisibility': False},
                               HTTP_AUTHORIZATION='Bearer ' + self.company_token)

        self.assertEqual(dict(res.data).get('phoneVisibility'),
                         False)
        self.assertEqual(res.status_code, 200)

        res = self.client.post(reverse('profile_edit'),
                               {'linkToCompany': 'https://linktocompany.com'},
                               HTTP_AUTHORIZATION='Bearer ' + self.company_token)

        self.assertEqual(dict(res.data).get('linkToCompany'),
                         'https://linktocompany.com')
        self.assertEqual(res.status_code, 200)

        res = self.client.post(reverse('profile_edit'),
                               {'firstName': 'Andrew'},
                               HTTP_AUTHORIZATION='Bearer ' + self.company_token)

        self.assertEqual(dict(res.data).get('firstName'),
                         '')
        self.assertEqual(res.status_code, 200)








