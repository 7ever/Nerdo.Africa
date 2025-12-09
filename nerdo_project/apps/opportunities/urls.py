from django.urls import path
from django.urls import path
from . import views

urlpatterns = [
    path('', views.job_market, name='job_market'),
    path('job/<int:pk>/', views.job_detail, name='job_detail'),
    path('my-jobs/', views.my_jobs, name='my_jobs'),
    path('reminder/<int:job_id>/', views.toggle_reminder, name='toggle_reminder'),
    path('apply/<int:pk>/', views.apply_job, name='apply_job'),
    path('create/', views.create_job, name='create_job'),
    path('job/update/<int:pk>/', views.update_job, name='update_job'),
    path('job/delete/<int:pk>/', views.delete_job, name='delete_job'),
]