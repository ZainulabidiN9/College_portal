from django import forms
from django.contrib.auth.models import User
from .models import Result


class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = ['student', 'course', 'total_marks', 'obtained_marks']

        widgets = {
            'total_marks': forms.NumberInput(attrs={'min': 0}),
            'obtained_marks': forms.NumberInput(attrs={'min': 0}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = User.objects.filter(
            is_superuser=False,
            is_staff=False,
        ).exclude(groups__name='teacher').distinct()

