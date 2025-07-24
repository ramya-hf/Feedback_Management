from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from accounts.models import User
from .models import Board, Feedback, Comment
import uuid

class FeedbackAPITestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(email='admin@test.com', password='admin123', role='admin')
        self.board = Board.objects.create(name='Board', description='Desc', slug='board', owner=self.admin)
        self.feedback = Feedback.objects.create(title='Test', description='Desc', board=self.board, author=self.admin)
        self.client.force_authenticate(user=self.admin)

    def test_feedback_list(self):
        url = reverse('feedback-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('results' in response.data or isinstance(response.data, list))

    def test_feedback_create(self):
        url = reverse('feedback-list')
        data = {
            'title': 'New Feedback',
            'description': 'Desc',
            'board': str(self.board.id),
            'category': 'feature',
            'priority': 'medium',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['title'], 'New Feedback')

    def test_feedback_vote(self):
        url = reverse('feedback-vote', args=[self.feedback.id])
        data = {'vote_type': 'upvote'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.feedback.refresh_from_db()
        self.assertEqual(self.feedback.vote_count, 1)

    def test_feedback_status_transition(self):
        url = reverse('feedback-set-status', args=[self.feedback.id])
        data = {'status': 'completed'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.feedback.refresh_from_db()
        self.assertEqual(self.feedback.status, 'completed')

    def test_feedback_filtering(self):
        url = reverse('feedback-list') + '?status=completed'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

class CommentAPITestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(email='admin@test.com', password='admin123', role='admin')
        self.board = Board.objects.create(name='Board', description='Desc', slug='board', owner=self.admin)
        self.feedback = Feedback.objects.create(title='Test', description='Desc', board=self.board, author=self.admin)
        self.comment = Comment.objects.create(content='Root comment', feedback=self.feedback, author=self.admin)
        self.reply = Comment.objects.create(content='Reply comment', feedback=self.feedback, author=self.admin, parent=self.comment)
        self.client.force_authenticate(user=self.admin)

    def test_comment_list(self):
        url = reverse('comment-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('results' in response.data or isinstance(response.data, list))

    def test_comment_create(self):
        url = reverse('comment-list')
        data = {
            'content': 'New comment',
            'feedback': str(self.feedback.id),
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['content'], 'New comment')

    def test_nested_comment_create(self):
        url = reverse('comment-list')
        data = {
            'content': 'Reply to comment',
            'feedback': str(self.feedback.id),
            'parent': str(self.comment.id),
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['parent'], str(self.comment.id))

    def test_comment_vote(self):
        url = reverse('comment-vote', args=[self.comment.id])
        data = {'vote_type': 'upvote'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.vote_count, 1)

    def test_comment_moderation(self):
        url = reverse('comment-moderate', args=[self.comment.id])
        data = {'is_active': False}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.comment.refresh_from_db()
        self.assertFalse(self.comment.is_active)

# Create your tests here.
