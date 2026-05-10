from django import forms
from .models import Participant, Feedback, Event


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ['student_id', 'name', 'email', 'event']
        widgets = {
            'student_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. CS2024001',
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'student@college.edu',
            }),
            'event': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_student_id(self):
        sid = self.cleaned_data['student_id'].strip().upper()
        if Participant.objects.filter(student_id=sid).exists():
            raise forms.ValidationError(
                "⚠ This Student ID is already registered. Each student may register only once."
            )
        return sid

    def clean_email(self):
        return self.cleaned_data['email'].strip().lower()


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['rating', 'comments']
        widgets = {
            'rating': forms.RadioSelect(attrs={'class': 'star-radio'}),
            'comments': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your experience with this event...',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].label = 'Rate your experience'
        self.fields['comments'].label = 'Additional comments (optional)'
        self.fields['comments'].required = False
