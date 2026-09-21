from django.db import models
from django.contrib.auth.models import User
from academics.models import course


class Result(models.Model):
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    course = models.ForeignKey(
        course,
        on_delete=models.CASCADE
    )

    total_marks = models.PositiveIntegerField(default=100)
    obtained_marks = models.PositiveIntegerField(default=0)

    def percentage(self):
        if self.total_marks == 0:
            return 0

        return round(
            (self.obtained_marks / self.total_marks) * 100,
            2
        )

    def grade(self):
        percentage = self.percentage()

        if percentage >= 80:
            return "A+"
        elif percentage >= 70:
            return "A"
        elif percentage >= 60:
            return "B"
        elif percentage >= 50:
            return "C"
        elif percentage >= 40:
            return "D"
        else:
            return "F"

    def status(self):
        if self.percentage() >= 40:
            return "Pass"
        return "Fail"

    def __str__(self):
        return f"{self.student.username} - {self.course.name}"