from django.urls import path
from . import views

urlpatterns = [
path('register/', views.register, name='register'),
path('login/', views.user_login, name='login'),
path('dashboard/', views.dashboard, name='dashboard'),
path('submit-complaint/', views.submit_complaint, name='submit_complaint'),
path('my-complaints/', views.my_complaints, name='my_complaints'),
path('logout/', views.user_logout, name='logout'),
path('departments/', views.department_information, name='departments'),

path('notifications/', views.notifications_list, name='notifications'),

path('staff-dashboard/', views.staff_dashboard, name='staff_dashboard'),
path(
    'update-complaint-status/<int:complaint_id>/',
    views.update_complaint_status,
    name='update_complaint_status'
),
path(
    'delete-complaint/<int:complaint_id>/',
    views.delete_complaint,
    name='delete_complaint'
),
path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),


]
