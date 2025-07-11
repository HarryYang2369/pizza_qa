from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class StudentRegistrationForm(UserCreationForm):
    real_name = forms.CharField(max_length=100, label="Full Name")
    email = forms.EmailField(label="School Email")
    year = forms.IntegerField(
        min_value=9, 
        max_value=12,
        label="Year of Study",
        help_text="(9-12)"
    )
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput,
        help_text="Your password must contain at least 8 characters."
    )
    password2 = forms.CharField(
        label="Password Confirmation",
        strip=False,
        widget=forms.PasswordInput,
        help_text="Enter the same password as before, for verification."
    )

    class Meta:
        model = CustomUser
        fields = ('real_name', 'email', 'year', 'password1', 'password2')
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'student'
        if commit:
            user.save()
        return user

class TeacherRegistrationForm(UserCreationForm):
    real_name = forms.CharField(max_length=100, label="Full Name")
    email = forms.EmailField(label="School Email")
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label="Password Confirmation",
        strip=False,
        widget=forms.PasswordInput
    )

    class Meta:
        model = CustomUser
        fields = ('real_name', 'email', 'password1', 'password2')
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'teacher'
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)