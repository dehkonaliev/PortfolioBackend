from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from .models import CustomUser


class PublicProfileAccessTests(APITestCase):
    def setUp(self):
        self.other_user = CustomUser.objects.create_user(
            username='owner',
            password='Testpass123!',
            first_name='Owner',
            last_name='User',
        )
        self.viewer = CustomUser.objects.create_user(
            username='viewer',
            password='Testpass123!',
        )

    def test_anonymous_can_view_profile_by_username(self):
        response = self.client.get(f'/api/user/{self.other_user.username}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['username'], 'owner')

    def test_anonymous_can_view_profile_by_id(self):
        response = self.client.get(f'/api/user/{self.other_user.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['username'], 'owner')

    def test_anonymous_can_list_projects(self):
        response = self.client.get('/api/projects/')
        self.assertEqual(response.status_code, 200)

    def test_anonymous_cannot_create_project(self):
        response = self.client.post('/api/projects/', {'name': 'x'}, format='multipart')
        self.assertEqual(response.status_code, 401)

    def test_owner_can_create_project(self):
        self.client.force_authenticate(self.other_user)
        response = self.client.post('/api/projects/', {'name': 'My project'}, format='multipart')
        self.assertEqual(response.status_code, 201)

