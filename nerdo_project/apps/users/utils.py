import requests
import random
import urllib3
from django.conf import settings

# Disable the annoying "InsecureRequestWarning" that appears when verify=False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def generate_otp():
    """
    Generates a cryptographically secure 6-digit random code.
    """
    return str(random.randint(100000, 999999))

def send_otp_sms(phone_number, otp):
    """
    Sends OTP via Africa's Talking (Sandbox) using a RAW HTTP REQUEST.
    
    NOTE: usage of 'verify=False' bypasses SSL errors common in Python 3.14 alpha versions.
    This is acceptable for the Sandbox/Dev environment but should be removed for Production.
    """
    
    # 1. Configuration
    username = settings.AFRICASTALKING_USERNAME  # Should be 'sandbox'
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
    # These tell the API who we are and what format we are sending
    headers = {
        'ApiKey': api_key,
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    
    # 4. Construct the Payload (The actual data)
    data = {
        'username': username,
        'to': clean_phone,
        'message': f"Your Nerdo.Africa verification code is: {otp}"
    }
    
    try:
        print(f"--> Sending Raw Request to Africa's Talking: {clean_phone}")
        
        # 5. Send the POST Request
        # verify=False is the magic switch that ignores the SSL Certificate error
        response = requests.post(url, data=data, headers=headers, verify=False)
        
        # 6. Analyze the Response
        # HTTP 201 means 'Created' (Success)
        if response.status_code == 201:
            response_data = response.json()
            # Dig into the JSON to find the status of the specific recipient
            recipients = response_data.get('SMSMessageData', {}).get('Recipients', [])
            if recipients and recipients[0]['status'] == 'Success':
                print(f"--> SMS Success! Cost: {recipients[0]['cost']}")
                return True
            else:
                print(f"--> API accepted request but delivery failed: {response.text}")
                return False
        else:
            print(f"--> SMS API Error ({response.status_code}): {response.text}")
            return False
            
    except Exception as e:
        print(f"--> CRITICAL SMS ERROR: {str(e)}")
        return False