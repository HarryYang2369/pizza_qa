from django.contrib import admin
from .models import YearGroup, Question, Answer

@admin.register(YearGroup)
class YearGroupAdmin(admin.ModelAdmin):
    list_display = ('year',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'year_group', 'created_at', 'resolved')
    search_fields = ('title', 'description')
    list_filter = ('year_group', 'resolved')

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('text', 'user', 'question', 'created_at')
    search_fields = ('text',)