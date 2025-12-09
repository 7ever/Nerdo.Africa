from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    email = forms.EmailField(required=True)
    
    # 1. Add Phone Number field (Required for OTP)
    phone_number = forms.CharField(
        max_length=15, 
        required=True, 
        help_text="Required for account recovery (e.g. +2547...)"
    )
    
    ROLE_CHOICES = [
        ('job_seeker', 'I am a Job Seeker'),
        ('employer', 'I am an Employer'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect, initial='job_seeker')

    ajira_id = forms.CharField(
        max_length=20, 
        required=False, 
        help_text="Optional: Enter your Ajira ID to get the Verified Badge."
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone_number', 'ajira_id']

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
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Save Phone Number to Profile
            user.profile.phone_number = self.cleaned_data.get('phone_number')
            user.profile.ajira_id = self.cleaned_data.get('ajira_id')
            user.profile.role = self.cleaned_data.get('role')
            
            if user.profile.ajira_id:
                user.profile.is_verified = True 
            else:
                user.profile.is_verified = False
            
            # Set Employer Verification to False explicitly (pending)
            if user.profile.role == 'employer':
                user.profile.is_employer_verified = False

            user.profile.save()
        return user

class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = Profile
        fields = ['avatar', 'phone_number', 'bio', 'cv'] # Added CV (FileField)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.save()
            # Update User model fields
            if self.cleaned_data.get('first_name'):
                profile.user.first_name = self.cleaned_data['first_name']
            if self.cleaned_data.get('last_name'):
                profile.user.last_name = self.cleaned_data['last_name']
            profile.user.save()
        return profile

class EmployerProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, label="Company Contact First Name")
    last_name = forms.CharField(max_length=30, required=True, label="Company Contact Last Name")
    
    class Meta:
        model = Profile
        fields = ['avatar', 'phone_number', 'location', 'website', 'bio', 
                  'social_twitter', 'social_linkedin', 'social_facebook']
        widgets = {
             'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us about your company...'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            
        # Add Bootstrap classes and placeholders
        for field in self.fields:
             if 'class' not in self.fields[field].widget.attrs:
                 self.fields[field].widget.attrs['class'] = 'form-control'
                 
        self.fields['location'].widget.attrs['placeholder'] = 'e.g. Nairobi, Kenya'

    def clean_website(self):
        url = self.cleaned_data.get('website')
        if url and not url.startswith(('http://', 'https://')):
            return f'https://{url}'
        return url

    def clean_social_twitter(self):
        url = self.cleaned_data.get('social_twitter')
        if url and not url.startswith(('http://', 'https://')):
            return f'https://{url}'
        return url

    def clean_social_linkedin(self):
        url = self.cleaned_data.get('social_linkedin')
        if url and not url.startswith(('http://', 'https://')):
            return f'https://{url}'
        return url

    def clean_social_facebook(self):
        url = self.cleaned_data.get('social_facebook')
        if url and not url.startswith(('http://', 'https://')):
            return f'https://{url}'
        return url

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.save()
            # Update User model fields
            if self.cleaned_data.get('first_name'):
                profile.user.first_name = self.cleaned_data['first_name']
            if self.cleaned_data.get('last_name'):
                profile.user.last_name = self.cleaned_data['last_name']
            profile.user.save()
        return profile

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