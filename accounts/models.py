from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class AuthActivity(models.Model):
	LOGIN = 'login'
	SIGNUP = 'signup'
	ACTION_CHOICES = [
		(LOGIN, 'Login'),
		(SIGNUP, 'Signup'),
	]

	user = models.ForeignKey(User, on_delete=models.CASCADE)
	action = models.CharField(max_length=10, choices=ACTION_CHOICES)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f'{self.user.username} - {self.get_action_display()}'
