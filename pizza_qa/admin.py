from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import CustomUser
from qa.models import YearGroup, Question, Answer

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'real_name', 'role', 'year', 'nickname', 'is_staff')
    search_fields = ('email', 'real_name', 'nickname')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('real_name', 'role', 'year', 'nickname')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'real_name', 'role', 'password1', 'password2'),
        }),
    )

class YearGroupAdmin(admin.ModelAdmin):
    list_display = ('year',)
    search_fields = ('year',)

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'year_group', 'created_at', 'resolved', 'visible_to_teachers')
    search_fields = ('title', 'description')
    list_filter = ('year_group', 'resolved', 'visible_to_teachers')
    raw_id_fields = ('student',)

class AnswerAdmin(admin.ModelAdmin):
    list_display = ('truncated_text', 'user', 'question', 'created_at', 'anonymous')
    search_fields = ('text',)
    list_filter = ('anonymous',)
    raw_id_fields = ('user', 'question')
    
    def truncated_text(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    truncated_text.short_description = 'Answer'

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(YearGroup, YearGroupAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)