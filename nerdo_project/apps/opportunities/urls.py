from django.urls import path
from . import views

urlpatterns = [
    path('', views.job_market, name='job_market'),
    path('create/', views.create_job, name='create_job'),
    path('job/<int:pk>/', views.job_detail, name='job_detail'),
    path('job/update/<int:pk>/', views.update_job, name='update_job'),
    path('job/delete/<int:pk>/', views.delete_job, name='delete_job'),
]