from django.contrib.auth.models import Group, User
from django.contrib.staticfiles import finders
from django.test import TestCase

from academics.models import course
from attendance.models import Attendance
from results.models import Result
from .models import AuthActivity


class AuthenticationActivityTests(TestCase):
	def test_staff_dashboard_counts_students_and_directory_searches_them(self):
		student_group = Group.objects.create(name='student')
		amina = User.objects.create_user(
			username='amina',
			first_name='Amina',
			email='amina@example.com',
		)
		amina.groups.add(student_group)
		bilal = User.objects.create_user(
			username='bilal',
			first_name='Bilal',
			email='bilal@example.com',
		)
		bilal.groups.add(student_group)
		admin = User.objects.create_superuser(username='admin', password='password123')
		self.client.force_login(admin)

		dashboard_response = self.client.get('/')
		directory_response = self.client.get('/students/?q=Amina')

		self.assertEqual(dashboard_response.context['student_count'], 2)
		self.assertContains(dashboard_response, 'student-directory')
		self.assertEqual(directory_response.status_code, 200)
		self.assertContains(directory_response, 'amina@example.com')
		self.assertNotContains(directory_response, 'bilal@example.com')

	def test_student_cannot_access_student_directory(self):
		student = User.objects.create_user(username='student', password='password123')
		student.groups.add(Group.objects.create(name='student'))
		self.client.force_login(student)

		response = self.client.get('/students/')

		self.assertEqual(response.status_code, 403)

	def test_dashboard_includes_student_metrics_and_chart_data(self):
		student = User.objects.create_user(username='student', password='password123')
		student.groups.add(Group.objects.create(name='student'))
		biology = course.objects.create(name='Biology', code='BIO101', teacher='Dr. Khan')
		Attendance.objects.create(
			student=student,
			course=biology,
			total_classes=10,
			present_classes=8,
			absent_classes=2,
		)
		Result.objects.create(
			student=student,
			course=biology,
			total_marks=100,
			obtained_marks=90,
		)
		self.client.force_login(student)

		response = self.client.get('/')

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context['course_count'], 1)
		self.assertEqual(response.context['attendance_percentage'], 80)
		self.assertEqual(response.context['average_score'], 90)
		self.assertEqual(response.context['chart_data']['labels'], ['Biology'])
		self.assertContains(response, 'course-chart')
		self.assertContains(response, 'gsap@3.13.0')

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

	def test_portal_css_is_discoverable(self):
		self.assertTrue(finders.find('portal.css'))
