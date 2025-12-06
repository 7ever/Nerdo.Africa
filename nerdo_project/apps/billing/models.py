from django.db import models
from django.contrib.auth.models import User

class MpesaTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    receipt_number = models.CharField(max_length=20, null=True, blank=True)
    status = models.CharField(max_length=20, default='Pending') # Pending, Success, Failed
    transaction_date = models.DateTimeField(auto_now_add=True)
    merchant_request_id = models.CharField(max_length=100, null=True, blank=True)
    checkout_request_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.status}"