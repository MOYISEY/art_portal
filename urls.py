from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('projects/', views.project_list, name='project_list'),
    path('projects/create/', views.project_create, name='project_create'),
    path('projects/<slug:slug>/', views.project_detail, name='project_detail'),
    path('projects/<slug:slug>/update/', views.project_update, name='project_update'),
    path('projects/<slug:slug>/delete/', views.project_delete, name='project_delete'),
    path('projects/like/<int:project_id>/', views.project_like, name='project_like'),
]

