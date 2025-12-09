from django.urls import path
from . import views

urlpatterns = [
    path('', views.community_home, name='community_home'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/like/<int:pk>/', views.like_post, name='like_post'),
]
