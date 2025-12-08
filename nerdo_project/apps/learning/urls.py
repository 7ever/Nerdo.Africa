from django.urls import path
from . import views

urlpatterns = [
    path('', views.learning_home, name='learning_home'),
    path('search/', views.search_roadmap, name='search_roadmap'),
    path('roadmap/', views.roadmap_view, name='roadmap_view'),
    path('roadmap/<int:path_id>/', views.roadmap_view_id, name='roadmap_view_id'),
    path('history/', views.learning_history, name='learning_history'),
    path('quick-search/<str:topic>/', views.quick_search, name='quick_search'),
]
