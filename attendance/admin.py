from django.contrib import admin
from django.contrib import admin
from .models import Attendance
# Register your models here.



@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):

    list_display = (
        'student',
        'course',
        'total_classes',
        'present_classes',
        'absent_classes',
        'percentage',
    )