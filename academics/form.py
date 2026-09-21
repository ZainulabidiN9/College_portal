from django import forms
from .models import course, Timetable


class CourseForm(forms.ModelForm):
    class Meta:
        model = course
        fields = ['name', 'code', 'teacher', 'credits', 'description']

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter course name'
            }),

            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter course code'
            }),

            'teacher': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter teacher name'
            }),

            'credits': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter credit hours'
            }),

            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter course description',
                'rows': 4
            }),
        }


class TimetableForm(forms.ModelForm):
    class Meta:
        model = Timetable
        fields = ['course', 'day', 'start_time', 'end_time', 'room']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }