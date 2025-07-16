from django.urls import path
from . import views

app_name = 'qa'
urlpatterns = [
    path('', views.subject_selection, name='subject_selection'),
    path('subject/<int:subject_id>/', views.subject_qa, name='subject_qa'),
    path('ask/<int:subject_id>/', views.ask_question, name='ask_question'),
    path('question/<int:question_id>/', views.question_detail, name='question_detail'),
    path('resolve/<int:question_id>/', views.mark_resolved, name='mark_resolved'),
    path('edit-question/<int:question_id>/', views.edit_question, name='edit_question'),
    path('delete-question/<int:question_id>/', views.delete_question, name='delete_question'),
    
    # Answer management
    path('edit-answer/<int:answer_id>/', views.edit_answer, name='edit_answer'),
    path('delete-answer/<int:answer_id>/', views.delete_answer, name='delete_answer'),
    
    # Subject management
    path('teacher-subjects/', views.manage_teacher_subjects, name='manage_teacher_subjects'),
    path('student-subjects/', views.manage_student_subjects, name='manage_student_subjects'),
    
    path('get_teachers/', views.get_teachers, name='get_teachers'),
]