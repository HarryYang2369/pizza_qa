"""Define URL patterns for the users app"""
from django.urls import path
from . import views

app_name = 'users'  # Add this line to register the namespace

urlpatterns = [
    path('register/student/', views.register_student, name='register_student'),
    #path('register/teacher/', views.register_teacher, name='register_teacher'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('management/', views.student_management, name='student_management'),
    path('delete/<int:student_id>/', views.delete_student, name='delete_student'),
]