from django.db import models
from django.db import models
from django.contrib.auth.models import User


class Teacher(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    subject = models.CharField(max_length=100)

    qualification = models.CharField(
        max_length=100,
        blank=True
    )

    phone = models.CharField(
        max_length=20,
        blank=True
    )

    def __str__(self):
        return self.user.username
# Create your models here.
