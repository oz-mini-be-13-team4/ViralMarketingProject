from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "nickname", "name", "is_active", "is_staff")
    search_fields = ("email", "nickname", "name")
    ordering = ("email",)
