from django.urls import path
from . import views

urlpatterns = [
    path('pay/', views.pay_premium, name='pay_premium'),
    path('callback/', views.mpesa_callback, name='mpesa_callback'),
]