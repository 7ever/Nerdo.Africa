from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django import forms
from django.db.models import Q
from .forms import UserRegisterForm, OTPVerifyForm, ProfileUpdateForm, EmployerProfileUpdateForm
from .models import Profile
from apps.opportunities.models import Job, Application 
from .utils import generate_otp, send_otp_sms
import random
from django.db.models import Count

# === LOCAL FORMS FOR PASSWORD RESET FLOW ===
class IdentifyUserForm(forms.Form):
    identifier = forms.CharField(
        label="Username or Email",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username or email'})
    )

class PhoneCheckForm(forms.Form):
    phone_number = forms.CharField(
        label="Phone Number",
        help_text="Enter the full phone number associated with your account.",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+254...'})
    )

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', '').strip()
        # 1. Enforce +254 format as requested
        if phone.startswith('07') or phone.startswith('01'):
            raise forms.ValidationError("Invalid format. Please use the Africa's Talking format starting with +254 (e.g., +254712...).")
        if not phone.startswith('+254'):
            raise forms.ValidationError("Phone number must start with +254.")
        return phone

# 1. Registration
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            # Basic User Data
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1'] 
            
            # Additional Fields
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone = form.cleaned_data['phone_number']
            ajira_id = form.cleaned_data['ajira_id']
            role = form.cleaned_data['role']
            
            # --- UNIQUE PHONE CHECK (Manual enforcement in View) ---
            if Profile.objects.filter(phone_number=phone).exists():
                messages.error(request, "This phone number is already registered to another account.")
                return render(request, 'users/register.html', {'form': form})

            otp = generate_otp()
            
            request.session['reg_data'] = {
                'username': username,
                'email': email,
                'password': password,
                'first_name': first_name,
                'last_name': last_name,
                'phone_number': phone,
                'ajira_id': ajira_id,
                'role': role
            }
            request.session['reg_otp'] = otp
            
            # Removed debug prints here
            
            send_otp_sms(phone, otp)
            messages.info(request, f"Verification code sent to {phone}")
            return redirect('verify_otp')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

# 2. OTP Verification View
def verify_otp(request):
    reg_data = request.session.get('reg_data')
    reg_otp = request.session.get('reg_otp')
    
    if not reg_data or not reg_otp:
        messages.error(request, "Session expired. Please sign up again.")
        return redirect('register')
    
    if request.method == 'POST':
        form = OTPVerifyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['otp_code']
            
            if code == reg_otp:
                try:
                    # Create User with First/Last Name
                    user = User.objects.create_user(
                        username=reg_data['username'],
                        email=reg_data['email'],
                        password=reg_data['password'],
                        first_name=reg_data['first_name'],
                        last_name=reg_data['last_name']
                    )
                    
                    # Update Profile
                    user.profile.phone_number = reg_data['phone_number']
                    user.profile.ajira_id = reg_data['ajira_id']
                    user.profile.role = reg_data['role']
                    user.profile.is_phone_verified = True
                    
                    if reg_data['ajira_id']:
                        user.profile.is_verified = True
                    
                    # Handle Employer Status
                    if reg_data['role'] == 'employer':
                        user.profile.is_employer_verified = False # Pending Admin Approval
                        messages.warning(request, "Account created! As an employer, your account requires Admin approval before posting jobs.")
                    else:
                        messages.success(request, "Account created successfully!")

                    user.profile.save()
                    
                    login(request, user)
                    
                    del request.session['reg_data']
                    del request.session['reg_otp']
                    
                    if user.profile.role == 'employer':
                        return redirect('employer_dashboard')
                    else:
                        return redirect('profile') # Go to User Dashboard

                except IntegrityError:
                    messages.error(request, "Username or email already taken.")
                    return redirect('register')
            else:
                # NOTIFICATION ON WRONG OTP
                messages.error(request, "Invalid verification code. Please check your SMS and try again.")
    else:
        form = OTPVerifyForm()
    
    return render(request, 'users/verify_otp.html', {'form': form})

@login_required
def profile(request):
    """
    User Dashboard for Job Seekers.
    Displays:
    - Profile Stats/Edit
    - My Applications
    - Recommended Jobs
    """
    user = request.user
    
    # Redirect Employers to their dashboard
    if hasattr(user, 'profile') and user.profile.role == 'employer':
        return redirect('employer_dashboard')

    if request.method == 'POST':
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=user.profile, user=user)
        if p_form.is_valid():
            p_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        p_form = ProfileUpdateForm(instance=user.profile, user=user)

    # 1. Get User's Applications
    my_applications = Application.objects.filter(applicant=user).select_related('job').order_by('-applied_at')

    # 2. Recommended Jobs (Logic: Same category as user's last application, or just recent jobs)
    # Simple logic: Latest 3 jobs matching a default category or just latest 3
    # For now, let's just show latest 3 jobs. 
    # Improvement: Filter by skills/category if we had that data in Profile.
    recommended_jobs = Job.objects.filter(is_approved=True).exclude(applications__applicant=user).select_related('author').order_by('-created_at')[:3]

    context = {
        'p_form': p_form,
        'my_applications': my_applications,
        'recommended_jobs': recommended_jobs,
    }
    return render(request, 'users/profile.html', context)

@login_required
def employer_dashboard(request):
    """
    Dashboard for Employers to manage their jobs.
    """
    user = request.user
    if not hasattr(user, 'profile') or user.profile.role != 'employer':
        messages.error(request, "Access denied. Employer account required.")
        return redirect('profile')

    if request.method == 'POST':
        # Handle Profile Update
        p_form = EmployerProfileUpdateForm(request.POST, request.FILES, instance=user.profile, user=user)
        if p_form.is_valid():
            p_form.save()
            messages.success(request, "Company profile updated successfully!")
            return redirect('employer_dashboard')
    else:
        p_form = EmployerProfileUpdateForm(instance=user.profile, user=user)

    my_jobs = Job.objects.filter(author=user).annotate(app_count=Count('applications')).order_by('-created_at')
    
    context = {
        'my_jobs': my_jobs,
        'p_form': p_form,
        'is_verified': user.profile.is_employer_verified
    }
    return render(request, 'users/employer_dashboard.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')

# === PASSWORD RESET FLOW (FIXED & IMPROVED) ===

def password_reset_request(request):
    stage = request.session.get('reset_stage', 'identify')
    
    # Allow manual reset of flow via query param
    if request.GET.get('start_over'):
        if 'reset_stage' in request.session: del request.session['reset_stage']
        if 'reset_temp_user_id' in request.session: del request.session['reset_temp_user_id']
        stage = 'identify'

    if stage == 'identify':
        # Step 1: User enters Username/Email
        if request.method == 'POST':
            form = IdentifyUserForm(request.POST)
            if form.is_valid():
                identifier = form.cleaned_data['identifier']
                
                # Check for Username OR Email
                user = User.objects.filter(Q(username=identifier) | Q(email=identifier)).first()
                
                if user:
                    if hasattr(user, 'profile') and user.profile.phone_number:
                        # Success: Move to next stage
                        request.session['reset_temp_user_id'] = user.id
                        request.session['reset_stage'] = 'phone_check'
                        return redirect('password_reset')
                    else:
                        messages.error(request, "This account does not have a linked phone number for recovery.")
                else:
                    messages.error(request, "Account with this username or email does not exist.")
        else:
            form = IdentifyUserForm()
        
        return render(request, 'users/password_reset_request.html', {
            'form': form, 
            'stage': 'identify',
            'title': 'Reset Password',
            'instruction': 'Enter your registered username or email to find your account.'
        })

    elif stage == 'phone_check':
        # Step 2: User confirms Phone Number
        user_id = request.session.get('reset_temp_user_id')
        if not user_id:
            return redirect('password_reset')
            
        user = User.objects.get(id=user_id)
        real_phone = user.profile.phone_number
        
        # Mask the phone number (e.g., *********1234)
        masked_phone = f"*********{real_phone[-4:]}" if len(real_phone) >= 4 else "********"

        if request.method == 'POST':
            form = PhoneCheckForm(request.POST)
            if form.is_valid():
                input_phone = form.cleaned_data['phone_number']
                
                # Verify match (exact string match since validation enforces +254)
                if input_phone.strip() == real_phone.strip():
                    otp = generate_otp()
                    user.profile.otp_code = otp
                    user.profile.save()
                    
                    # Removed debug prints here
                    
                    send_otp_sms(real_phone, otp)
                    
                    request.session['reset_phone'] = real_phone
                    
                    # Clear stage session data
                    del request.session['reset_stage']
                    del request.session['reset_temp_user_id']
                    
                    messages.info(request, f"OTP sent to {masked_phone}. Please verify.")
                    return redirect('password_reset_verify')
                else:
                    messages.error(request, "That is not the correct registered phone number.")
        else:
            form = PhoneCheckForm()
            # Informative message for context
            messages.info(request, f"We found your account. For security, confirm the number ending in {masked_phone}")

        return render(request, 'users/password_reset_request.html', {
            'form': form, 
            'stage': 'phone_check',
            'title': 'Verify Phone Number',
            'instruction': f'For security, please enter the full phone number ending with {masked_phone}'
        })

def password_reset_verify(request):
    phone = request.session.get('reset_phone')
    if not phone:
        messages.error(request, "Session expired. Start over.")
        return redirect('password_reset')
        
    if request.method == 'POST':
        form = OTPVerifyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['otp_code']
            try:
                profile = Profile.objects.get(phone_number=phone)
                
                if profile.otp_code == code:
                    profile.otp_code = None 
                    profile.save()
                    
                    request.session['reset_user_id'] = profile.user.id
                    return redirect('password_reset_confirm')
                else:
                    # NOTIFICATION ON WRONG OTP
                    messages.error(request, "Invalid OTP code. Please try again.")
            except Profile.DoesNotExist:
                messages.error(request, "Error verifying user.")
    else:
        form = OTPVerifyForm()
    return render(request, 'users/password_reset_verify.html', {'form': form})

def password_reset_confirm(request):
    user_id = request.session.get('reset_user_id')
    if not user_id:
        messages.error(request, "Unauthorized. Please verify OTP first.")
        return redirect('password_reset')
        
    user = User.objects.get(id=user_id)
    
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            
            if 'reset_phone' in request.session:
                del request.session['reset_phone']
            if 'reset_user_id' in request.session:
                del request.session['reset_user_id']
            
            messages.success(request, "Password reset successful! Please login.")
            return redirect('login')
    else:
        form = SetPasswordForm(user)
        
    return render(request, 'users/password_reset_confirm.html', {'form': form})