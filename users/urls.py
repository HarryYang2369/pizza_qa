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
    path('profile/', views.user_profile, name='user_profile'),
    path('teacher_profile/', views.teacher_profile, name='teacher_profile'),
    path('student_profile/<int:student_id>/<int:subject_id>/', views.student_profile, name='student_profile'),
    # path('view_student_profile/<int:student_id>/<int:subject_id>/', views.view_student_profile, name='view_student_profile'),
    path('manage-students/<int:subject_id>/', views.manage_students_in_subject, name='manage_students_in_subject'),
    path('manage-questions/<int:subject_id>/<str:question_type>/', views.manage_questions, name='manage_questions'),
    # path('student-questions/', views.student_questions, name='student_questions'),
    path('student-subject-questions/<int:subject_id>/', views.student_subject_questions, name='student_subject_questions'),
    path('change-password/', views.change_password, name='change_password'),
    path('teacher/classes/', views.teacher_class_selection, name='teacher_class_selection'),
    path('teacher/questions/', views.teacher_question_type_selection, name='teacher_question_type_selection'),
    path('teacher/questions/<str:question_type>/', views.teacher_subject_selection, name='teacher_subject_selection'),
    path('student/questions/<str:view_type>/', views.student_subject_selection, name='student_subject_selection'),
    path('student/questions/<int:subject_id>/<str:view_type>/', views.student_subject_questions, name='student_subject_questions'),
    path('student/answers/<int:subject_id>/<str:answer_type>/', views.student_answers, name='student_answers'),
]