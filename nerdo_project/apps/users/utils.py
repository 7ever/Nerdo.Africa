import africastalking
import random
from django.conf import settings

def generate_otp():
    """Generate a 6-digit random code"""
    return str(random.randint(100000, 999999))

def send_otp_sms(phone_number, otp):
    """
    Sends OTP via Africa's Talking (Sandbox).
    """
    username = settings.AFRICASTALKING_USERNAME
    api_key = settings.AFRICASTALKING_API_KEY

    # Initialize SDK
    africastalking.initialize(username, api_key)
    sms = africastalking.SMS

    message = f"Your Nerdo.Africa verification code is: {otp}"

    # Ensure phone format is +254... for Africa's Talking
    clean_phone = str(phone_number).strip().replace(' ', '')
    if clean_phone.startswith('0'):
        clean_phone = '+254' + clean_phone[1:]
    elif clean_phone.startswith('254'):
        clean_phone = '+' + clean_phone

    try:
        # Enqueue=True is faster for bulk, but False is better for OTP (immediate)
        response = sms.send(message, [clean_phone])
        print(f"AT Response: {response}") # For Debugging
        return True
    except Exception as e:
        print(f"SMS Error: {e}")
        return False