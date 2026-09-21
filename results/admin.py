from django.contrib import admin 
from .models import Result


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):

    list_display = (
        'student',
        'course',
        'total_marks',
        'obtained_marks',
        'percentage',
        'grade',
        'status',
    )