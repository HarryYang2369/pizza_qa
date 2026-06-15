from django.contrib import admin
from .models import YearGroup, Question, Answer, Subject, Followup, Notification

@admin.register(YearGroup)
class YearGroupAdmin(admin.ModelAdmin):
    list_display = ('year',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'year_group', 'subject', 'created_at', 'resolved')
    search_fields = ('title', 'description')
    list_filter = ('year_group', 'resolved', 'subject')

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'text', 'user', 'created_at', 'subject')
    search_fields = ('text',)

    def subject(self, obj):
        return obj.question.subject if obj.question else None
    subject.short_description = 'Subject'

@admin.register(Followup)
class FollowupAdmin(admin.ModelAdmin):
    list_display = ('question', 'user', 'parent', 'created_at')
    search_fields = ('text',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'message', 'is_read', 'created_at')
    list_filter = ('is_read',)
    search_fields = ('message',)