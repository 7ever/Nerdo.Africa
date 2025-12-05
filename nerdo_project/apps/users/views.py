from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, PasswordResetRequestForm, OTPVerifyForm
from .models import Profile
import random

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now login.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return render(request, 'users/logout.html')

@login_required
def profile(request):
    return render(request, 'users/profile.html')

# === OTP PASSWORD RESET FLOW ===

def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone_number']
            # Find user with this phone
            # Note: In production, handle duplicates. For now, we assume unique.
            try:
                profile = Profile.objects.get(phone_number=phone)
                user = profile.user
                
                # 1. Generate OTP
                otp = str(random.randint(100000, 999999))
                profile.otp_code = otp
                profile.save()
                
                # 2. Send SMS (MOCKED FOR NOW)
                # Later, we will put Africa's Talking API code here
                print(f"------------")
                print(f"SMS TO {phone}: Your OTP is {otp}")
                print(f"------------")
                
                # 3. Store phone in session to pass to next step
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
                
                # Check OTP
                if profile.otp_code == code:
                    # Success! Allow password reset
                    # We store the user ID in session to allow the next step
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
            # Clean up session
            del request.session['reset_phone']
            del request.session['reset_user_id']
            # Clear OTP
            user.profile.otp_code = None
            user.profile.save()
            
            messages.success(request, "Password reset successful! You can now login.")
            return redirect('login')
    else:
        form = SetPasswordForm(user)
        
    return render(request, 'users/password_reset_confirm.html', {'form': form})