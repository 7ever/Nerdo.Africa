from django.urls import path
from . import views

urlpatterns = [
    path('', views.job_market, name='job_market'),
    path('create/', views.create_job, name='create_job'),
    path('job/<int:pk>/', views.job_detail, name='job_detail'),
]