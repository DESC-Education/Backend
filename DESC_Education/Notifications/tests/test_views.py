from rest_framework.test import APITestCase
from django.urls import reverse
from Users.models import CustomUser
from Notifications.models import Notification

class ReadNotificationViewTest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(email='example@mail.ru',
                                                   password='test_password',
                                                   is_verified=True)
        self.notification = Notification.objects.create(user=self.user, title='Test notification')

    def test_view_200(self):
        res = self.client.get(reverse('read_notification', args=[self.notification.id]),
                              HTTP_AUTHORIZATION=f'Bearer {self.user.get_token()["accessToken"]}')


        self.assertTrue(dict(res.data).get('isRead'))
        self.assertEqual(res.status_code, 200)
