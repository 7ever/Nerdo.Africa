from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.conf import settings # Import settings to debug keys
from django_daraja.mpesa.core import MpesaClient
from .models import MpesaTransaction
from .forms import PaymentForm
import json

@login_required
def pay_premium(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            # 1. INPUT HANDLING
            raw_phone = form.cleaned_data['phone_number']
            
            # 2. ROBUST SANITIZATION
            # Strip spaces, dashes, plus signs
            phone_number = str(raw_phone).strip().replace(' ', '').replace('-', '').replace('+', '')
            
            # Convert 07xx/01xx to 2547xx/2541xx
            if phone_number.startswith('0'):
                phone_number = '254' + phone_number[1:]
            elif not phone_number.startswith('254'):
                phone_number = '254' + phone_number
            
            # 3. DEBUGGING (Check your terminal!)
            print(f"-------- M-PESA DEBUG --------")
            print(f"Target Phone: {phone_number}")
            print(f"Consumer Key Loaded? {'Yes' if settings.MPESA_CONSUMER_KEY else 'NO (Check .env)'}")
            
            amount = 1
            # Sanitize Account Reference (Remove spaces, limit to 12 chars)
            clean_username = request.user.username.replace(' ', '')
            account_reference = f'Nerdo_{clean_username}'[:12]
            transaction_desc = 'PremiumVerification' # No spaces to be safe
            
            callback_url = 'http://mysite.com/billing/callback' 

            cl = MpesaClient()
            try:
                # 4. INITIATE STK PUSH
                print(f"Sending request to Safaricom...")
                response = cl.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)
                
                print(f"Safaricom Response Code: {response.response_code}")
                print(f"Safaricom Description: {response.response_description}")

                # Check if the push was successfully sent (Response Code '0')
                if response.response_code == '0':
                    MpesaTransaction.objects.create(
                        user=request.user,
                        phone_number=phone_number,
                        amount=amount,
                        merchant_request_id=response.merchant_request_id,
                        checkout_request_id=response.checkout_request_id,
                        status='Pending'
                    )
                    messages.success(request, f"STK Push sent to {phone_number}. Check your phone!")
                    return redirect('profile')
                else:
                    # Show the actual error from Safaricom to the user
                    messages.error(request, f"M-Pesa Failed: {response.response_description}")

            except Exception as e:
                print(f"EXCEPTION: {str(e)}")
                messages.error(request, f"System Error: {str(e)}")
                
    else:
        initial_data = {}
        if hasattr(request.user, 'profile') and request.user.profile.phone_number:
            initial_data['phone_number'] = request.user.profile.phone_number
        form = PaymentForm(initial=initial_data)

    return render(request, 'billing/pay_premium.html', {'form': form})

@csrf_exempt
def mpesa_callback(request):
    """
    Automated Database Update
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Log callback data to terminal to confirm reception
            print(f"CALLBACK DATA: {data}")
            
            stk_callback = data.get('Body', {}).get('stkCallback', {})
            checkout_request_id = stk_callback.get('CheckoutRequestID')
            result_code = stk_callback.get('ResultCode')
            result_desc = stk_callback.get('ResultDesc')
            
            transaction = MpesaTransaction.objects.get(checkout_request_id=checkout_request_id)

            if result_code == 0:
                transaction.status = 'Success'
                items = stk_callback.get('CallbackMetadata', {}).get('Item', [])
                for item in items:
                    if item.get('Name') == 'MpesaReceiptNumber':
                        transaction.receipt_number = item.get('Value')
                transaction.save()

                user_profile = transaction.user.profile
                user_profile.is_verified = True
                user_profile.save()
            else:
                transaction.status = 'Failed'
                transaction.save()

            return JsonResponse({"result": "ok"})
        except Exception as e:
            print(f"Callback Error: {e}")
            return JsonResponse({"result": "error"})

    return JsonResponse({"result": "ok"})