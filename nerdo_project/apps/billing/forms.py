from django import forms

class PaymentForm(forms.Form):
    phone_number = forms.CharField(
        max_length=15,
        label="M-Pesa Number",
        help_text="Enter the M-Pesa number to pay with (e.g., 0712345678)",
        widget=forms.TextInput(attrs={
            'placeholder': '07XX...',
            'class': 'form-control',
            'type': 'tel' # Optimizes keyboard on mobile
        })
    )