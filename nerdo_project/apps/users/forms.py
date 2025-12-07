from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    # 1. Add Phone Number field (Required for OTP)
    phone_number = forms.CharField(
        max_length=15, 
        required=True, 
        help_text="Required for account recovery (e.g. +2547...)"
    )
    
    ajira_id = forms.CharField(
        max_length=20, 
        required=False, 
        help_text="Optional: Enter your Ajira ID to get the Verified Badge."
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'ajira_id']

    # --- EMAIL VALIDATION ---
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered. Please login or use a different email.")
        return email

    # --- PHONE VALIDATION ---
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', '').strip()
        # Basic formatting check
        if phone.startswith('07') or phone.startswith('01'):
             raise forms.ValidationError("Please use the format +254...")
        if not phone.startswith('+254'):
             raise forms.ValidationError("Phone number must start with +254.")
             
        # Check uniqueness
        if Profile.objects.filter(phone_number=phone).exists():
            raise forms.ValidationError("This phone number is already registered.")
        return phone

    def clean_ajira_id(self):
        ajira_id = self.cleaned_data.get('ajira_id')
        if ajira_id and not ajira_id.upper().startswith('AJ-'):
            raise forms.ValidationError("Invalid Ajira ID format. Must start with 'AJ-'.")
        return ajira_id

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            # Save Phone Number to Profile
            user.profile.phone_number = self.cleaned_data.get('phone_number')
            user.profile.ajira_id = self.cleaned_data.get('ajira_id')
            
            if user.profile.ajira_id:
                user.profile.is_verified = True 
            else:
                user.profile.is_verified = False
                
            user.profile.save()
        return user

# 2. Form for Requesting the Reset (Enter Phone)
class PasswordResetRequestForm(forms.Form):
    phone_number = forms.CharField(max_length=15, label="Enter Registered Phone Number")

# 3. Form for Verifying OTP
class OTPVerifyForm(forms.Form):
    otp_code = forms.CharField(
        max_length=6, 
        label="Verification Code",
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center text-spacing-4', 
            'placeholder': '123456',
            'autocomplete': 'off'
        })
    )