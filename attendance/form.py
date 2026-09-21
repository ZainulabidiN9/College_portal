from django import forms
from django.contrib.auth.models import User
from .models import Attendance


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['student', 'course', 'total_classes', 'present_classes', 'absent_classes']

        widgets = {
            'total_classes': forms.NumberInput(attrs={'min': 0}),
            'present_classes': forms.NumberInput(attrs={'min': 0}),
            'absent_classes': forms.NumberInput(attrs={'min': 0}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = User.objects.filter(
            is_superuser=False,
            is_staff=False,
        ).exclude(groups__name='teacher').distinct()

