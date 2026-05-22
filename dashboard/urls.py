from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('students/', views.student_list_view, name='student_list'),
    path('students/add/', views.add_student_view, name='add_student'),
    path('students/edit/<int:pk>/', views.edit_student_view, name='edit_student'),
    path('students/delete/<int:pk>/', views.delete_student_view, name='delete_student'),
    path('attendance/', views.mark_attendance_view, name='mark_attendance'),
    path('courses/', views.course_list_view, name='course_list'),
    path('courses/add/', views.add_course_view, name='add_course'),
    path('courses/edit/<int:pk>/', views.edit_course_view, name='edit_course'),
    path('courses/delete/<int:pk>/', views.delete_course_view, name='delete_course'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('support/', views.support_view, name='support'),
]
