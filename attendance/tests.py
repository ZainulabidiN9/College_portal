from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from academics.models import course
from .form import AttendanceForm
from .models import Attendance


class AttendanceValidationTests(TestCase):
	def setUp(self):
		self.student = User.objects.create_user(username='student')
		self.course = course.objects.create(
			name='Mathematics',
			code='MATH101',
			teacher='Teacher',
		)

	def test_model_rejects_inconsistent_class_counts(self):
		record = Attendance(
			student=self.student,
			course=self.course,
			total_classes=10,
			present_classes=8,
			absent_classes=1,
		)

		with self.assertRaises(ValidationError):
			record.full_clean()

	def test_form_rejects_inconsistent_class_counts(self):
		form = AttendanceForm(data={
			'student': self.student.pk,
			'course': self.course.pk,
			'total_classes': 10,
			'present_classes': 8,
			'absent_classes': 1,
		})

		self.assertFalse(form.is_valid())
		self.assertIn('Present and absent classes', str(form.errors))

	def test_percentage_uses_consistent_counts(self):
		record = Attendance(
			student=self.student,
			course=self.course,
			total_classes=10,
			present_classes=8,
			absent_classes=2,
		)

		self.assertEqual(record.percentage(), 80.0)
