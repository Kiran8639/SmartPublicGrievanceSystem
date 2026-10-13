from django import forms
from .models import Complaint

class ComplaintForm(forms.ModelForm):
 class Meta:
    model = Complaint
    fields = ['title', 'description', 'location', 'department', 'priority', 'photo']


    widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Example: Pothole near the main road'
            }),
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Describe the civic problem in detail'
            }),
            'location': forms.TextInput(attrs={
                'placeholder': 'Enter area, street, or landmark'
            }),
        }

