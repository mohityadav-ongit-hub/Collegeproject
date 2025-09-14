# gym_app/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import MembershipPlan, Member, Payment, FreeTrial

class CustomUserCreationForm(UserCreationForm):
    phone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'placeholder': 'Enter phone number', 'class': 'form-input'}),
        error_messages={'required': 'Phone number is required.'}
    )
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
        error_messages={'required': 'Date of birth is required.'}
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Enter address', 'class': 'form-input'}),
        error_messages={'required': 'Address is required.'}
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Enter email', 'class': 'form-input'}),
        error_messages={'required': 'Email is required.'}
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'phone', 'date_of_birth', 'address']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Enter username', 'class': 'form-input'}),
            'password1': forms.PasswordInput(attrs={'placeholder': 'Enter password', 'class': 'form-input'}),
            'password2': forms.PasswordInput(attrs={'placeholder': 'Confirm password', 'class': 'form-input'}),
        }

class FreeTrialForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter password', 'class': 'form-input'}),
        required=True,
        error_messages={'required': 'Password is required.'}
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password', 'class': 'form-input'}),
        required=True,
        error_messages={'required': 'Password confirmation is required.'}
    )

    class Meta:
        model = FreeTrial
        fields = ['username', 'password', 'confirm_password', 'phone', 'date_of_birth', 'address']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Enter username', 'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Enter phone number', 'class': 'form-input'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'address': forms.Textarea(attrs={'placeholder': 'Enter address', 'class': 'form-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned_data

class MembershipPlanForm(forms.ModelForm):
    class Meta:
        model = MembershipPlan
        fields = ['name', 'duration_months', 'price', 'description']

class MemberPlanForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['membership_plan']
        widgets = {'membership_plan': forms.Select()}

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'status']

class AgeForm(forms.Form):
    age = forms.IntegerField(
        min_value=15,
        max_value=70,
        required=True,
        error_messages={
            'required': 'Age is required.',
            'invalid': 'Please enter a valid age.',
            'min_value': 'Age must be greater than or equal to 15.',
            'max_value': 'Age must be less than or equal to 70.'
        },
        widget=forms.NumberInput(attrs={'placeholder': 'Enter your age (15–70)', 'class': 'age-input'})
    )

class AdminLoginForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter admin password', 'class': 'admin-password-input'}),
        required=True,
        error_messages={'required': 'Password is required.'}
    )