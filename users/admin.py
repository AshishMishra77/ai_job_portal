from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User

    # Fields to display in admin list view
    list_display = ("username", "email", "role", "experience", "is_staff", "is_active")

    # Filters in right sidebar
    list_filter = ("role", "is_staff", "is_active")

    # Field grouping in admin detail page
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Additional Info", {
            "fields": ("role", "resume", "skills", "experience"),
        }),
    )

    # Fields when creating a new user
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Additional Info", {
            "fields": ("role", "resume", "skills", "experience"),
        }),
    )

    # Search functionality
    search_fields = ("username", "email", "role")

    # Ordering
    ordering = ("username",)