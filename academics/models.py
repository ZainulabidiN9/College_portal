from django.db import models

# Create your models here.

class course(models.Model):
    
    name= models.CharField(max_length=100)
    code= models.CharField(max_length=20)
    teacher= models.CharField(max_length=100)
    credits= models.PositiveIntegerField(default=3)
    description= models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} - {self.code}"




class Timetable(models.Model):

    DAYS = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
    ]

    course = models.ForeignKey(
        course,
        on_delete=models.CASCADE
    )

    day = models.CharField(
        max_length=20,
        choices=DAYS
    )

    start_time = models.TimeField()
    end_time = models.TimeField()

    room = models.CharField(
        max_length=50,
        blank=True
    )

    def __str__(self):
        return f"{self.course.name} - {self.day}"