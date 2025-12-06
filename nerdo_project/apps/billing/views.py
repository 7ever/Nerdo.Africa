from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django_daraja.mpesa.core import MpesaClient
from .models import MpesaTransaction
from .forms import PaymentForm
import json

@login_required
def pay_premium(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            # 1. CAPTURE INPUT: Get the number explicitly from the form
            raw_phone = form.cleaned_data['phone_number']
            
            # 2. SANITIZE: Format to 254... (M-Pesa Requirement)
            # Remove spaces, dashes, plus signs
            phone_number = str(raw_phone).strip().replace(' ', '').replace('-', '').replace('+', '')
            
            # Ensure proper prefix (e.g., 0722 -> 254722)
            if phone_number.startswith('0'):
                phone_number = '254' + phone_number[1:]
            elif not phone_number.startswith('254'):
                phone_number = '254' + phone_number
            
            # Debugging: Print to terminal to verify what is being sent
            print(f"DEBUG: Processing Payment for sanitized number: {phone_number}")

            amount = 1
            # Note: AccountReference has a 12-char limit in Sandbox. 
            # We truncate to avoid 'Bad Request' errors.
            account_reference = f'Nerdo_{request.user.username}'[:12]
            transaction_desc = 'Premium Verification'
            
            # Note: Update this with your ngrok/live URL for callbacks to actually update the DB
            callback_url = 'http://127.0.0.1:8000/billing/callback/' 

            cl = MpesaClient()
            try:
                # 3. INITIATE STK PUSH
                response = cl.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)
                
                # Check if the push was successfully sent to the phone (Response Code '0')
                if response.response_code == '0':
                    # Save transaction to DB as 'Pending'
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
                    messages.error(request, f"M-Pesa Error: {response.response_description}")

            except Exception as e:
                messages.error(request, f"System Error: {str(e)}")
                print(f"Error: {e}")
                
    else:
        # Pre-fill form with profile number if it exists (Convenience only)
        initial_data = {}
        if hasattr(request.user, 'profile') and request.user.profile.phone_number:
            initial_data['phone_number'] = request.user.profile.phone_number
        form = PaymentForm(initial=initial_data)

    return render(request, 'billing/pay_premium.html', {'form': form})

@csrf_exempt
def mpesa_callback(request):
    """
    Automated Database Update:
    1. Receives JSON from Safaricom.
    2. Checks if payment was successful (ResultCode 0).
    3. Updates Transaction status.
    4. Automatically grants Premium status (is_verified) to the User.
    """
    if request.method == 'POST':
        try:
            # 1. Parse the incoming JSON data
            data = json.loads(request.body)
            stk_callback = data.get('Body', {}).get('stkCallback', {})
            
            merchant_request_id = stk_callback.get('MerchantRequestID')
            checkout_request_id = stk_callback.get('CheckoutRequestID')
            result_code = stk_callback.get('ResultCode')
            result_desc = stk_callback.get('ResultDesc')

            # 2. Find the transaction in OUR database
            transaction = MpesaTransaction.objects.get(checkout_request_id=checkout_request_id)

            if result_code == 0:
                # === SUCCESSFUL PAYMENT ===
                transaction.status = 'Success'
                
                # Extract Receipt Number (MpesaReceiptNumber)
                items = stk_callback.get('CallbackMetadata', {}).get('Item', [])
                for item in items:
                    if item.get('Name') == 'MpesaReceiptNumber':
                        transaction.receipt_number = item.get('Value')
                
                transaction.save()

                # === AUTOMATICALLY UPDATE USER PROFILE ===
                # Grant Premium / Verified Status
                user_profile = transaction.user.profile
                user_profile.is_verified = True
                user_profile.save()
                
                print(f"Payment Success: {transaction.receipt_number}. User {transaction.user.username} is now Verified.")

            else:
                # === FAILED PAYMENT ===
                transaction.status = 'Failed'
                transaction.save()
                print(f"Payment Failed: {result_desc}")

            return JsonResponse({"result": "ok"})

        except MpesaTransaction.DoesNotExist:
            print("Error: Transaction not found for this callback.")
            return JsonResponse({"result": "error", "message": "Transaction not found"})
        except Exception as e:
            print(f"Callback Error: {str(e)}")
            return JsonResponse({"result": "error", "message": str(e)})

    return JsonResponse({"result": "ok"})