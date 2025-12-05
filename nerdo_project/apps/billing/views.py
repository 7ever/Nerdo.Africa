from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django_daraja.mpesa.core import MpesaClient
from .models import MpesaTransaction
import json

@login_required
def pay_premium(request):
    if request.method == 'POST':
        # 1. Get Phone from Profile (Created in Issue 2)
        phone_number = request.user.profile.phone_number
        if not phone_number:
            messages.error(request, "Please update your profile with a phone number first.")
            return redirect('profile')

        # 2. Format Phone Number (Basic Sanitization)
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        elif phone_number.startswith('+'):
            phone_number = phone_number[1:]

        # 3. Setup Payment Data
        amount = 1 # KES 1 for testing
        account_reference = f'NerdoPremium_{request.user.id}'
        transaction_desc = 'Premium Verification Badge'
        # Note: For local dev, this callback won't be hit unless you use ngrok
        callback_url = 'https://mydomain.com/billing/callback' 

        cl = MpesaClient()
        try:
            # 4. Initiate STK Push
            response = cl.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)

            # 5. Save Transaction Record
            MpesaTransaction.objects.create(
                user=request.user,
                phone_number=phone_number,
                amount=amount,
                merchant_request_id=response.merchant_request_id,
                checkout_request_id=response.checkout_request_id,
                status='Pending'
            )

            messages.success(request, f"STK Push sent to {phone_number}. Enter PIN to complete.")
            return redirect('profile')

        except Exception as e:
            messages.error(request, f"Error initiating payment: {str(e)}")

    return render(request, 'billing/pay_premium.html')

@csrf_exempt
def mpesa_callback(request):
    """
    Receives the JSON payload from Safaricom after the user enters their PIN.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # In a real app, you parse 'Body.stkCallback.ResultCode' here
            # 0 means success, other numbers mean cancelled/failed
            return JsonResponse({"result": "ok"})
        except Exception as e:
            return JsonResponse({"result": "error", "message": str(e)})
    return JsonResponse({"result": "ok"})