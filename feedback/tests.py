from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from accounts.models import User
from .models import Board
import uuid

class BoardAPITestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(email='admin@test.com', password='admin123', role='admin')
        self.moderator = User.objects.create_user(email='mod@test.com', password='mod123', role='moderator')
        self.contributor = User.objects.create_user(email='user@test.com', password='user123', role='contributor')
        self.board = Board.objects.create(name='Test Board', description='Board Desc', slug='test-board', owner=self.admin)
        self.board.moderators.add(self.moderator)
        self.board.members.add(self.contributor)

    def test_board_list(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('board-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('results' in response.data or isinstance(response.data, list))

    def test_board_create(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('board-list')
        data = {
            'name': 'New Board',
            'description': 'Desc',
            'slug': 'new-board',
            'visibility': 'public',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], 'New Board')

    def test_add_member(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('board-add-member', args=[self.board.id])
        new_user = User.objects.create_user(email='new@test.com', password='new123', role='contributor')
        data = {'user_id': str(new_user.id)}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(new_user, self.board.members.all())

    def test_remove_member(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('board-remove-member', args=[self.board.id])
        data = {'user_id': str(self.contributor.id)}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.contributor, self.board.members.all())

    def test_permissions(self):
        self.client.force_authenticate(user=self.contributor)
        url = reverse('board-destroy', args=[self.board.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)
