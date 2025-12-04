from django.urls import path
from . import views

urlpatterns = [
    path('', views.job_market, name='job_market'),
]