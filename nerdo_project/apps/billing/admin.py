from django.contrib import admin
from .models import MpesaTransaction

@admin.register(MpesaTransaction)
class MpesaTransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'phone_number', 'status', 'transaction_date')
    list_filter = ('status', 'transaction_date')