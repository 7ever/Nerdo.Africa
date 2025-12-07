from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from .forms import UserRegisterForm, PasswordResetRequestForm, OTPVerifyForm
from .models import Profile
from .utils import generate_otp, send_otp_sms
import random

# 1. Registration (PRE-SAVE Verification)
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            # STRICT EXCEPTION: Do not save to DB yet.
            # We extract data to store in Session (Server-side temporary storage)
            
            # Cleaned data contains the validated input
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone_number']
            ajira_id = form.cleaned_data['ajira_id']
            # UserCreationForm uses 'password1' for the primary password field
            password = form.cleaned_data['password1'] 
            
            # 1. Generate OTP
            otp = generate_otp()
            
            # 2. Store Registration Data & OTP in Session
            # This keeps it in memory/session DB, not the main User table
            request.session['reg_data'] = {
                'username': username,
                'email': email,
                'password': password,
                'phone_number': phone,
                'ajira_id': ajira_id
            }
            request.session['reg_otp'] = otp
            
            # 3. Send SMS
            print(f"\n{'='*40}")
            print(f"NERDO DEBUG: Verification Code for {phone} is {otp}")
            print(f"{'='*40}\n")
            
            if send_otp_sms(phone, otp):
                messages.info(request, f"Verification code sent to {phone}")
                return redirect('verify_otp')
            else:
                messages.warning(request, "SMS failed. Please try again or check number.")
                # In production, you might stop here. For dev, we proceed so you can see the console debug.
                return redirect('verify_otp')
                
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

# 2. OTP Verification View (Commit to DB)
def verify_otp(request):
    # Check if we have pending registration data
    reg_data = request.session.get('reg_data')
    reg_otp = request.session.get('reg_otp')
    
    if not reg_data or not reg_otp:
        messages.error(request, "Session expired or no pending registration. Please sign up again.")
        return redirect('register')
    
    if request.method == 'POST':
        form = OTPVerifyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['otp_code']
            
            # Verify Logic
            if code == reg_otp:
                try:
                    # === CRITICAL STEP: CREATE ACCOUNT ===
                    # Only now do we write to the User table
                    user = User.objects.create_user(
                        username=reg_data['username'],
                        email=reg_data['email'],
                        password=reg_data['password']
                    )
                    
                    # Update the automatically created profile (from signals)
                    user.profile.phone_number = reg_data['phone_number']
                    user.profile.ajira_id = reg_data['ajira_id']
                    user.profile.is_phone_verified = True
                    
                    # Grant Ajira Verification if ID was provided
                    if reg_data['ajira_id']:
                        user.profile.is_verified = True
                        
                    user.profile.save()
                    
                    # Log User In
                    login(request, user)
                    
                    # Clean Session
                    del request.session['reg_data']
                    del request.session['reg_otp']
                    if 'verification_user_id' in request.session:
                        del request.session['verification_user_id']
                    
                    messages.success(request, "Account created and verified successfully! Welcome to Nerdo.")
                    return redirect('job_market')

                except IntegrityError:
                    # Rare edge case: Someone took the username while user was entering OTP
                    messages.error(request, "Error: This username or email was taken just now. Please try again.")
                    return redirect('register')
            else:
                messages.error(request, "Invalid code. Please try again.")
    else:
        form = OTPVerifyForm()
        
    return render(request, 'users/verify_otp.html', {'form': form})

# 3. Profile View
@login_required
def profile(request):
    return render(request, 'users/profile.html')

# 4. Logout View
def logout_view(request):
    logout(request)
    return render(request, 'users/logout.html')

# 5. Password Reset Flow (Logic remains mostly the same, handling existing users)
def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone_number']
            try:
                profile = Profile.objects.get(phone_number=phone)
                
                # OTP for Reset
                otp = generate_otp()
                
                # We store OTP in profile because the user ALREADY exists here
                profile.otp_code = otp
                profile.save()
                
                print(f"\n{'='*40}")
                print(f"NERDO DEBUG: Password Reset OTP for {phone} is {otp}")
                print(f"{'='*40}\n")
                
                send_otp_sms(phone, otp)
                
                request.session['reset_phone'] = phone
                messages.info(request, "OTP sent to your phone. Please verify.")
                return redirect('password_reset_verify')
                
            except Profile.DoesNotExist:
                messages.error(request, "No account found with that phone number.")
    else:
        form = PasswordResetRequestForm()
    return render(request, 'users/password_reset_request.html', {'form': form})

def password_reset_verify(request):
    phone = request.session.get('reset_phone')
    if not phone:
        return redirect('password_reset_request')
        
    if request.method == 'POST':
        form = OTPVerifyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['otp_code']
            try:
                profile = Profile.objects.get(phone_number=phone)
                
                if profile.otp_code == code:
                    request.session['reset_user_id'] = profile.user.id
                    return redirect('password_reset_confirm')
                else:
                    messages.error(request, "Invalid OTP code.")
            except Profile.DoesNotExist:
                messages.error(request, "Error verifying user.")
    else:
        form = OTPVerifyForm()
    return render(request, 'users/password_reset_verify.html', {'form': form})

def password_reset_confirm(request):
    user_id = request.session.get('reset_user_id')
    if not user_id:
        return redirect('password_reset_request')
        
    user = User.objects.get(id=user_id)
    
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            del request.session['reset_phone']
            del request.session['reset_user_id']
            user.profile.otp_code = None
            user.profile.save()
            
            messages.success(request, "Password reset successful! You can now login.")
            return redirect('login')
    else:
        form = SetPasswordForm(user)
        
    return render(request, 'users/password_reset_confirm.html', {'form': form})