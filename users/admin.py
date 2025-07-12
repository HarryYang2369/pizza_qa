from django.contrib import admin
from .models import CustomUser

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'real_name', 'role', 'year', 'nickname', 'is_active')
    list_filter = ('role', 'year', 'is_active')
    search_fields = ('email', 'real_name', 'nickname')
    actions = ['delete_selected']

admin.site.register(CustomUser, CustomUserAdmin)