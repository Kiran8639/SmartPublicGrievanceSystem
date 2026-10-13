from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CitizenRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)


    class Meta:
        model = User
        fields = ['username', 'password1', 'password2','email']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.USER

        if commit:
            user.save()

        return user

 