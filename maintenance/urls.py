from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='maintenance/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    path('complaint/new/', views.create_complaint, name='create_complaint'),
    path('complaint/<str:ticket_id>/', views.complaint_detail, name='complaint_detail'),
    path('complaint/<str:ticket_id>/allocate/', views.allocate_job, name='allocate_job'),
    path('complaint/<str:ticket_id>/status/<str:new_status>/', views.update_status, name='update_status'),
    path('complaint/<str:ticket_id>/close/', views.verify_and_close, name='verify_and_close'),
]
