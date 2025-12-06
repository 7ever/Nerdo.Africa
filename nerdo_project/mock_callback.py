import requests

# 1. The URL of your local callback view
URL = "http://127.0.0.1:8000/billing/callback/"

# 2. Paste the REAL ID you copied from Admin here
REAL_CHECKOUT_ID = "PASTE_YOUR_COPIED_ID_HERE"

# 3. The Mock Data (Success)
payload = {
    "Body": {
        "stkCallback": {
            "MerchantRequestID": "mock-123",
            "CheckoutRequestID": REAL_CHECKOUT_ID,
            "ResultCode": 0,
            "ResultDesc": "Success",
            "CallbackMetadata": {
                "Item": [
                    {"Name": "Amount", "Value": 1.00},
                    {"Name": "MpesaReceiptNumber", "Value": "OC12345678"},
                    {"Name": "PhoneNumber", "Value": 254712345678}
                ]
            }
        }
    }
}

# 4. Send the Fake "Success" Signal
requests.post(URL, json=payload)
print("Mock Callback Sent!")