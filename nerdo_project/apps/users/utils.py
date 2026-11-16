import requests
import secrets
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def generate_otp():
    return str(secrets.randbelow(900000) + 100000)

def send_sms(phone_number, message):
    """
    Generic SMS sender using Africa's Talking (Sandbox).
    Replaces old 'send_otp_sms'.
    
    NOTE: usage of 'verify=False' bypasses SSL errors common in Python 3.14 alpha versions.
    This is acceptable for the Sandbox/Dev environment but should be removed for Production.
    """
    
    # 1. Configuration
    username = settings.AFRICASTALKING_USERNAME 
    api_key = settings.AFRICASTALKING_API_KEY
    
    # The endpoint specific to the Sandbox environment
    url = "https://api.sandbox.africastalking.com/version1/messaging"
    
    # 2. Sanitization (Crucial Step)
    # The API requires phone numbers in the format +254...
    clean_phone = str(phone_number).strip().replace(' ', '').replace('-', '')
    
    if clean_phone.startswith('0'):
        # Convert 0712... to +254712...
        clean_phone = '+254' + clean_phone[1:]
    elif clean_phone.startswith('254'):
        # Convert 254712... to +254712...
        clean_phone = '+' + clean_phone
    
    # 3. Construct the Request Headers
    headers = {
        'ApiKey': api_key,
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    
    # 4. Construct the Payload
    data = {
        'username': username,
        'to': clean_phone,
        'message': message
    }
    
    try:
        logger.debug("Sending SMS to %s", clean_phone)

        response = requests.post(url, data=data, headers=headers)

        if response.status_code == 201:
            response_data = response.json()
            recipients = response_data.get('SMSMessageData', {}).get('Recipients', [])
            if recipients and recipients[0]['status'] == 'Success':
                logger.info("SMS sent successfully. Cost: %s", recipients[0]['cost'])
                return True
            else:
                logger.warning("SMS API accepted but delivery failed: %s", response.text)
                return False
        else:
            logger.error("SMS API error %s: %s", response.status_code, response.text)
            return False

    except Exception as e:
        logger.error("SMS send failed: %s", e)
        return False

def send_otp_sms(phone_number, otp):
    """
    Wrapper for backward compatibility.
    """
    msg = f"Your Nerdo.Africa verification code is: {otp}"
    return send_sms(phone_number, msg)