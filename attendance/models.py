from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from academics.models import course
# Create your models here.



class Attendance(models.Model):

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    course = models.ForeignKey(
        course,
        on_delete=models.CASCADE
    )

    total_classes = models.PositiveIntegerField(default=0)
    present_classes = models.PositiveIntegerField(default=0)
    absent_classes = models.PositiveIntegerField(default=0)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    present_classes=models.F('total_classes') - models.F('absent_classes')
                ),
                name='attendance_present_plus_absent_matches_total',
            ),
        ]

    def clean(self):
        super().clean()
        if self.present_classes + self.absent_classes != self.total_classes:
            raise ValidationError(
                'Present and absent classes must add up to total classes.'
            )

    def percentage(self):

        if self.total_classes == 0:
            return 0

        return round(
            (self.present_classes / self.total_classes) * 100,
            2
        )

    def __str__(self):
        return f"{self.student.username} - {self.course.name}"