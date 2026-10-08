from django.urls import path
from . import views

urlpatterns = [
    path('',views.dashboad , name ='dashboard'),
    path('signup/',views.signup , name ='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/',views.profile , name ='profile'),
    path('students/', views.student_directory, name='student_directory'),
    path('student_dashboard/',views.student_dashboard , name ='student_dashboard'),
    path('teacher-dashboard/',views.teacher_dashboard,name='teacher_dashboard'),
    path('admin-dashboard/',views.admin_dashboard,name='admin_dashboard'),
    path('create-teacher/',views.create_teacher,name='create_teacher'),
    path('courses/', views.courses, name='courses'),
    path('attendance/', views.attendance, name='attendance'),
    path('results/', views.results, name='results'),
    path('timetable/', views.timetable, name='timetable'),
    path('attendance/add/', views.add_attendance, name='add_attendance'),
    path('attendance/edit/<int:id>/', views.edit_attendance, name='edit_attendance'),
    path('attendance/delete/<int:id>/', views.delete_attendance, name='delete_attendance'),
    path('results/add/', views.add_result, name='add_result'),
    path('results/edit/<int:id>/', views.edit_result, name='edit_result'),
    path('results/delete/<int:id>/', views.delete_result, name='delete_result'),
    path('timetable/add/', views.add_timetable, name='add_timetable'),
    path('timetable/edit/<int:id>/', views.edit_timetable, name='edit_timetable'),
    path('timetable/delete/<int:id>/', views.delete_timetable, name='delete_timetable'),
    
    ]
