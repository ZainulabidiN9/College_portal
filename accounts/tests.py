from django.contrib.auth.models import User
from django.test import TestCase

from .models import AuthActivity


class AuthenticationActivityTests(TestCase):
	def test_login_creates_a_new_activity_record_each_time(self):
		User.objects.create_user(username='student', password='password123')

		login_data = {'username': 'student', 'password': 'password123'}
		login_response = self.client.post('/login/', login_data)
		self.assertRedirects(login_response, '/')
		self.client.logout()
		second_login_response = self.client.post('/login/', login_data)
		self.assertRedirects(second_login_response, '/')

		self.assertEqual(
			AuthActivity.objects.filter(user__username='student', action=AuthActivity.LOGIN).count(),
			2,
		)

	def test_signup_creates_signup_activity_record(self):
		response = self.client.post(
			'/signup/',
			{
				'username': 'newstudent',
				'email': 'newstudent@example.com',
				'password1': 'StrongPassword123!',
				'password2': 'StrongPassword123!',
			},
		)

		self.assertRedirects(response, '/')
		self.assertTrue(
			AuthActivity.objects.filter(
				user__username='newstudent',
				action=AuthActivity.SIGNUP,
			).exists()
		)

	def test_portal_css_is_served(self):
		response = self.client.get('/static/portal.css')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response['Content-Type'], 'text/css')
