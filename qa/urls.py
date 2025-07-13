from django.urls import path
from . import views

app_name = 'qa'
urlpatterns = [
    path('', views.year_selection, name='year_selection'),
    path('year/<int:year_id>/', views.class_qa, name='class_qa'),
    path('ask/<int:year_id>/', views.ask_question, name='ask_question'),
    path('question/<int:question_id>/', views.question_detail, name='question_detail'),
    path('resolve/<int:question_id>/', views.mark_resolved, name='mark_resolved'),
    path('edit-question/<int:question_id>/', views.edit_question, name='edit_question'),
    path('delete-question/<int:question_id>/', views.delete_question, name='delete_question'),
    
    # Answer management
    path('edit-answer/<int:answer_id>/', views.edit_answer, name='edit_answer'),
    path('delete-answer/<int:answer_id>/', views.delete_answer, name='delete_answer'),
]